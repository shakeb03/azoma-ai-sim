export interface SimulateRequest {
  url: string;
}

export interface ScrapedListing {
  url: string;
  title: string;
  description: string;
  specs: Record<string, string>;
  raw_text: string;
  brand: string;
  category: string;
  price: string;
}

export type LLMPlatform = "chatgpt" | "gemini" | "claude" | "rufus";

export interface VariationResult {
  prompt: string;
  response_text: string;
  brand_mentioned: boolean;
  error?: string;
}

export interface LLMResponse {
  platform: LLMPlatform;
  model_id: string;
  response_text: string;
  brand_mentioned: boolean;
  mention_count: number;
  mention_rate: number;
  variation_responses: VariationResult[];
  error?: string;
}

export interface GapField {
  attribute: string;
  in_listing: boolean;
  in_chatgpt: boolean;
  in_gemini: boolean;
  in_claude: boolean;
  in_rufus: boolean;
  ground_truth_value?: string;
  notes?: string;
}

export interface GapReport {
  gap_fields: GapField[];
  hallucinations: string[];
  missing_attributes: string[];
  overall_accuracy_pct: number;
}

export interface VisibilityScore {
  score: number;
  overall_mention_rate: number;
  platform_rates: Record<string, number>;
  platforms_mentioned: string[];
  platforms_not_mentioned: string[];
}

export interface SimulateResponse {
  brand: string;
  product: string;
  scraped_listing: ScrapedListing;
  generated_prompts: string[];
  llm_responses: LLMResponse[];
  gap_report: GapReport;
  visibility_score: VisibilityScore;
  duration_ms: number;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public stage: string = "unknown"
  ) {
    super(message);
    this.name = "ApiError";
  }
}
