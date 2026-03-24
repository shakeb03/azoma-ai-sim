def build_analysis_prompt(
    brand: str,
    url: str,
    title: str,
    description: str,
    specs: dict[str, str],
    raw_text: str,
    responses: dict[str, str],
) -> str:
    specs_text = "\n".join(f"  {k}: {v}" for k, v in specs.items()) or "  (none extracted)"
    platforms = ["chatgpt", "gemini", "claude", "rufus"]
    platform_labels = {
        "chatgpt": "ChatGPT",
        "gemini": "Gemini",
        "claude": "Claude",
        "rufus": "Rufus (Amazon Shopping Assistant)",
    }

    responses_text = "\n\n".join(
        f"[{platform_labels[p]}]\n{responses.get(p, '(no response)')}"
        for p in platforms
    )

    return f"""GROUND TRUTH PRODUCT LISTING (from {brand}'s official website):
URL: {url}
Title: {title}
Description: {description}
Specifications:
{specs_text}
Full page text (truncated):
{raw_text[:3000]}

---

AI SHOPPING ASSISTANT RESPONSES:

{responses_text}

---

ANALYSIS TASK:
Compare each AI response against the ground truth. Identify:

1. gap_fields: For each key product attribute present in the listing (e.g. voltage, battery type, weight, warranty, model number, price range), determine whether each AI response mentioned it correctly.

2. hallucinations: List any specific claims made by any AI that directly contradict the ground truth listing (wrong specs, wrong model numbers, invented features).

3. missing_attributes: List key product attributes from the listing that NO AI response mentioned at all.

4. overall_accuracy_pct: A score 0-100 representing how well the AIs collectively covered the ground truth, weighted by attribute importance.

OUTPUT FORMAT (strict JSON, no markdown, no extra text):
{{
  "gap_fields": [
    {{
      "attribute": "string",
      "in_listing": true,
      "in_chatgpt": true,
      "in_gemini": false,
      "in_claude": true,
      "in_rufus": false,
      "ground_truth_value": "string or null",
      "notes": "string or null"
    }}
  ],
  "hallucinations": ["string"],
  "missing_attributes": ["string"],
  "overall_accuracy_pct": 75.0
}}"""
