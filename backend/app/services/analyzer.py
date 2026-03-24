import json
import re
from app.models import LLMResponse, ScrapedListing, GapReport, GapField, VisibilityScore
from app.prompts.analysis import build_analysis_prompt
from app.config import settings


def _brand_mentioned(brand: str, text: str) -> bool:
    """Case-insensitive check for brand name presence in a response."""
    return bool(brand) and bool(text) and brand.lower() in text.lower()


def _compute_mention_rates(brand: str, responses: list[LLMResponse]) -> None:
    """
    Compute mention_count, mention_rate, and brand_mentioned for each response
    using simple string matching across all variation_responses.
    Mutates the response objects in place.
    """
    for r in responses:
        if r.variation_responses:
            valid = [v for v in r.variation_responses if not v.error]
            mentions = [_brand_mentioned(brand, v.response_text) for v in valid]
            r.mention_count = sum(mentions)
            r.mention_rate = r.mention_count / len(mentions) if mentions else 0.0
        else:
            hit = _brand_mentioned(brand, r.response_text)
            r.mention_count = 1 if hit else 0
            r.mention_rate = float(r.mention_count)

        for v in r.variation_responses:
            v.brand_mentioned = _brand_mentioned(brand, v.response_text)

        r.brand_mentioned = r.mention_count > 0


async def analyze_responses(
    listing: ScrapedListing,
    responses: list[LLMResponse],
) -> tuple[GapReport, VisibilityScore]:
    """
    1. Compute brand mention rates via string matching (no extra LLM cost).
    2. Run a single LLM gap-analysis call using one representative response per platform.
    Returns GapReport and VisibilityScore.
    """
    brand = listing.brand

    # Step 1: mention rates
    _compute_mention_rates(brand, responses)

    # Step 2: gap analysis — use representative (first successful) text per platform
    response_map = {r.platform: r.response_text for r in responses}

    prompt = build_analysis_prompt(
        brand=brand,
        url=listing.url,
        title=listing.title,
        description=listing.description,
        specs=listing.specs,
        raw_text=listing.raw_text,
        responses=response_map,
    )

    raw_json = await _call_analysis_llm(prompt)
    data = _parse_json(raw_json)

    gap_fields = [GapField(**f) for f in data.get("gap_fields", [])]

    gap_report = GapReport(
        gap_fields=gap_fields,
        hallucinations=data.get("hallucinations", []),
        missing_attributes=data.get("missing_attributes", []),
        overall_accuracy_pct=float(data.get("overall_accuracy_pct", 0.0)),
    )

    # Step 3: build VisibilityScore from pre-computed rates
    platform_rates = {r.platform: round(r.mention_rate, 4) for r in responses}
    overall_rate = sum(platform_rates.values()) / len(platform_rates) if platform_rates else 0.0
    mentioned = [r.platform for r in responses if r.brand_mentioned]
    not_mentioned = [r.platform for r in responses if not r.brand_mentioned]

    visibility = VisibilityScore(
        score=len(mentioned),
        overall_mention_rate=round(overall_rate, 4),
        platform_rates=platform_rates,
        platforms_mentioned=mentioned,
        platforms_not_mentioned=not_mentioned,
    )

    return gap_report, visibility


async def _call_analysis_llm(prompt: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    resp = await client.chat.completions.create(
        model=settings.analysis_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a product listing accuracy analyst. "
                    "Return valid JSON only. No markdown, no extra text outside the JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=2000,
    )
    return resp.choices[0].message.content or "{}"


def _parse_json(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "gap_fields": [],
            "hallucinations": [],
            "missing_attributes": [],
            "overall_accuracy_pct": 0.0,
        }
