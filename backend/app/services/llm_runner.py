import asyncio
import re
from app.models import LLMResponse, VariationResult
from app.prompts.shopping import SYSTEM_PROMPTS
from app.config import settings


def _strip_markdown(text: str) -> str:
    """Remove common markdown syntax, returning plain prose."""
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.+?)_{1,3}", r"\1", text)
    text = re.sub(r"~~(.+?)~~", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\-\*\+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[-\*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _first_successful(variations: list[VariationResult]) -> str:
    """Return the response_text of the first non-error variation, or empty string."""
    return next((v.response_text for v in variations if not v.error and v.response_text), "")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def run_all_llms(user_msgs: list[str]) -> list[LLMResponse]:
    """
    Fire all 4 platforms simultaneously.
    Each platform receives the same list of pre-generated prompt variations.
    """
    results = await asyncio.gather(
        _call_chatgpt(user_msgs),
        _call_gemini(user_msgs),
        _call_claude(user_msgs),
        _call_rufus(user_msgs),
        return_exceptions=False,
    )
    return list(results)


# ---------------------------------------------------------------------------
# ChatGPT
# ---------------------------------------------------------------------------

async def _call_chatgpt_single(user_msg: str) -> VariationResult:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["chatgpt"]},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        text = resp.choices[0].message.content or ""
        return VariationResult(prompt=user_msg, response_text=text, brand_mentioned=False)
    except Exception as e:
        return VariationResult(prompt=user_msg, response_text="", brand_mentioned=False, error=str(e))


async def _call_chatgpt(user_msgs: list[str]) -> LLMResponse:
    variations = list(await asyncio.gather(*[_call_chatgpt_single(m) for m in user_msgs]))
    return LLMResponse(
        platform="chatgpt",
        model_id="gpt-4o",
        response_text=_first_successful(variations),
        brand_mentioned=False,
        variation_responses=variations,
    )


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------

async def _call_gemini_single(user_msg: str) -> VariationResult:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite",
            system_instruction=SYSTEM_PROMPTS["gemini"],
        )
        response = await asyncio.to_thread(
            model.generate_content,
            user_msg,
            generation_config={"temperature": 0.3, "max_output_tokens": 1000},
        )
        text = response.text or ""
        return VariationResult(prompt=user_msg, response_text=text, brand_mentioned=False)
    except Exception as e:
        return VariationResult(prompt=user_msg, response_text="", brand_mentioned=False, error=str(e))


async def _call_gemini(user_msgs: list[str]) -> LLMResponse:
    variations = list(await asyncio.gather(*[_call_gemini_single(m) for m in user_msgs]))
    return LLMResponse(
        platform="gemini",
        model_id="gemini-2.0-flash-lite",
        response_text=_first_successful(variations),
        brand_mentioned=False,
        variation_responses=variations,
    )


# ---------------------------------------------------------------------------
# Claude
# ---------------------------------------------------------------------------

async def _call_claude_single(user_msg: str) -> VariationResult:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        resp = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPTS["claude"],
            messages=[{"role": "user", "content": user_msg}],
        )
        text = _strip_markdown(resp.content[0].text if resp.content else "")
        return VariationResult(prompt=user_msg, response_text=text, brand_mentioned=False)
    except Exception as e:
        return VariationResult(prompt=user_msg, response_text="", brand_mentioned=False, error=str(e))


async def _call_claude(user_msgs: list[str]) -> LLMResponse:
    variations = list(await asyncio.gather(*[_call_claude_single(m) for m in user_msgs]))
    return LLMResponse(
        platform="claude",
        model_id="claude-sonnet-4-6",
        response_text=_first_successful(variations),
        brand_mentioned=False,
        variation_responses=variations,
    )


# ---------------------------------------------------------------------------
# Rufus
# ---------------------------------------------------------------------------

async def _call_rufus_single(user_msg: str) -> VariationResult:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["rufus"]},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        text = resp.choices[0].message.content or ""
        return VariationResult(prompt=user_msg, response_text=text, brand_mentioned=False)
    except Exception as e:
        return VariationResult(prompt=user_msg, response_text="", brand_mentioned=False, error=str(e))


async def _call_rufus(user_msgs: list[str]) -> LLMResponse:
    variations = list(await asyncio.gather(*[_call_rufus_single(m) for m in user_msgs]))
    return LLMResponse(
        platform="rufus",
        model_id="gpt-4o (rufus)",
        response_text=_first_successful(variations),
        brand_mentioned=False,
        variation_responses=variations,
    )
