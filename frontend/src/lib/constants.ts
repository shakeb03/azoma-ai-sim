import { LLMPlatform } from "./types";

export const PLATFORM_CONFIG: Record<
  LLMPlatform,
  { label: string; color: string; bgColor: string; borderColor: string }
> = {
  chatgpt: {
    label: "ChatGPT",
    color: "#10A37F",
    bgColor: "#f0fdf9",
    borderColor: "#10A37F",
  },
  gemini: {
    label: "Gemini",
    color: "#4285F4",
    bgColor: "#eff6ff",
    borderColor: "#4285F4",
  },
  claude: {
    label: "Claude",
    color: "#D97706",
    bgColor: "#fffbeb",
    borderColor: "#D97706",
  },
  rufus: {
    label: "Rufus",
    color: "#FF9900",
    bgColor: "#fff7ed",
    borderColor: "#FF9900",
  },
};

export const LOADING_STAGES = [
  { key: "scraping",    label: "Scraping product page..." },
  { key: "generating",  label: "Generating prompt variations with AI..." },
  { key: "querying",    label: "Running 5 prompts × 4 AI platforms..." },
  { key: "analyzing",   label: "Running gap analysis..." },
] as const;

export type LoadingStage = (typeof LOADING_STAGES)[number]["key"];
