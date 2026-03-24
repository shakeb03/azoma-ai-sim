from pydantic import BaseModel, Field
from typing import Optional, Literal


class SimulateRequest(BaseModel):
    url: str = Field(..., min_length=10, examples=["https://www.canadiantire.ca/en/..."])


class ScrapedListing(BaseModel):
    url: str
    title: str
    description: str
    specs: dict[str, str]
    raw_text: str
    # Populated by the prompt-generation LLM after scraping
    brand: str = ""
    category: str = ""
    price: str = ""


class VariationResult(BaseModel):
    """Result for a single prompt variation sent to one platform."""
    prompt: str
    response_text: str
    brand_mentioned: bool
    error: Optional[str] = None


class LLMResponse(BaseModel):
    platform: Literal["chatgpt", "gemini", "claude", "rufus"]
    model_id: str
    response_text: str           # representative response (first successful variation)
    brand_mentioned: bool        # True if at least one variation mentioned the brand
    mention_count: int = 0       # how many of the 5 variations mentioned the brand
    mention_rate: float = 0.0    # mention_count / total_variations  (0.0 – 1.0)
    variation_responses: list[VariationResult] = []
    error: Optional[str] = None


class GapField(BaseModel):
    attribute: str
    in_listing: bool
    in_chatgpt: bool
    in_gemini: bool
    in_claude: bool
    in_rufus: bool
    ground_truth_value: Optional[str] = None
    notes: Optional[str] = None


class GapReport(BaseModel):
    gap_fields: list[GapField]
    hallucinations: list[str]
    missing_attributes: list[str]
    overall_accuracy_pct: float


class VisibilityScore(BaseModel):
    score: int                          # number of platforms with at least 1 mention (0-4)
    overall_mention_rate: float         # average mention_rate across all platforms (0.0-1.0)
    platform_rates: dict[str, float]    # e.g. {"chatgpt": 0.8, "gemini": 0.4, ...}
    platforms_mentioned: list[str]
    platforms_not_mentioned: list[str]


class SimulateResponse(BaseModel):
    brand: str
    product: str
    scraped_listing: ScrapedListing
    generated_prompts: list[str]
    llm_responses: list[LLMResponse]
    gap_report: GapReport
    visibility_score: VisibilityScore
    duration_ms: int


class ErrorResponse(BaseModel):
    detail: str
    stage: Literal["scraping", "prompt_generation", "llm_calls", "analysis", "unknown"]
