"""
Single LLM call that does two jobs from the scraped listing:
  1. Extracts structured metadata: brand, category, price
  2. Generates 5 natural, category-level shopping prompts

"Category-level" means prompts a real shopper would type into an AI assistant
without knowing or mentioning the specific brand — e.g. "best cordless drill
under $150 for home use", NOT "What does Canadian Tire sell for drills?".
This lets us measure whether the brand surfaces organically.
"""

import json
import re
from app.models import ScrapedListing
from app.config import settings


_SYSTEM = (
    "You are a product research assistant. "
    "Return valid JSON only. No markdown, no text outside the JSON object."
)

_PROMPT_TEMPLATE = """
Below is data scraped from a product listing page. Use it to complete two tasks.

SCRAPED DATA
------------
Title: {title}
Description: {description}
Specs: {specs}
Page text (truncated): {raw_text}

TASKS
-----
1. Extract:
   - brand: the brand or retailer name (string)
   - category: a short, lowercase, generic product category — e.g. "cordless drill", "running shoes", "espresso machine" (string)
   - price: the price if visible, otherwise "" (string)

2. Generate exactly 5 natural shopping prompts a consumer might type into an AI assistant
   (ChatGPT, Gemini, etc.) when searching for this type of product.
   Rules:
   - CATEGORY-LEVEL only: do NOT mention the brand name or specific model
   - Vary the style across the 5: feature-focused, use-case, budget, comparison, buying-guide
   - Sound like a real shopper, not a product description

OUTPUT FORMAT (strict JSON, no extra keys):
{{
  "brand": "string",
  "category": "string",
  "price": "string",
  "prompts": [
    "prompt 1",
    "prompt 2",
    "prompt 3",
    "prompt 4",
    "prompt 5"
  ]
}}
"""


async def extract_and_generate(listing: ScrapedListing) -> tuple[str, str, str, list[str]]:
    """
    Returns (brand, category, price, prompts).
    Also patches those fields directly onto the listing object.
    """
    specs_text = "; ".join(f"{k}: {v}" for k, v in listing.specs.items()) or "(none)"
    prompt = _PROMPT_TEMPLATE.format(
        title=listing.title,
        description=listing.description[:800],
        specs=specs_text[:600],
        raw_text=listing.raw_text[:2000],
    )

    raw = await _call_llm(prompt)
    data = _parse_json(raw)

    brand = data.get("brand", "") or ""
    category = data.get("category", "") or ""
    price = data.get("price", "") or ""
    prompts: list[str] = data.get("prompts", [])

    # Ensure exactly 5 prompts; pad with a fallback if the LLM returns fewer
    while len(prompts) < 5:
        prompts.append(f"What should I look for in a {category or 'product'} like this?")
    prompts = prompts[:5]

    # Patch the listing in place so downstream code has the enriched object
    listing.brand = brand
    listing.category = category
    listing.price = price

    return brand, category, price, prompts


async def _call_llm(prompt: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    resp = await client.chat.completions.create(
        model=settings.analysis_model,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
        max_tokens=800,
    )
    return resp.choices[0].message.content or "{}"


def _parse_json(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"brand": "", "category": "", "price": "", "prompts": []}
