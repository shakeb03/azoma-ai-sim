"use client";

import { useState } from "react";
import { LLMResponse } from "@/lib/types";
import { PLATFORM_CONFIG } from "@/lib/constants";

interface Props {
  response: LLMResponse;
}

function mentionRateColor(rate: number): string {
  if (rate >= 0.8) return "bg-green-100 text-green-700";
  if (rate >= 0.4) return "bg-yellow-100 text-yellow-700";
  return "bg-gray-100 text-gray-500";
}

export default function AIResponseCard({ response }: Props) {
  const config = PLATFORM_CONFIG[response.platform];
  const [showVariations, setShowVariations] = useState(false);

  const totalVariations = response.variation_responses.length;
  const mentionPct = Math.round(response.mention_rate * 100);
  const mentionLabel =
    totalVariations > 0
      ? `${response.mention_count}/${totalVariations} (${mentionPct}%)`
      : response.brand_mentioned
      ? "Mentioned"
      : "Not mentioned";

  return (
    <div
      className="flex flex-col rounded-xl border-2 overflow-hidden bg-white shadow-sm"
      style={{ borderColor: config.borderColor }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{ backgroundColor: config.bgColor }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: config.color }}
          />
          <span className="font-semibold text-gray-900">{config.label}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 font-mono bg-white/70 px-2 py-0.5 rounded">
            {response.model_id}
          </span>
          {response.error && !totalVariations ? (
            <span className="text-xs font-medium bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
              Error
            </span>
          ) : (
            <span
              className={`text-xs font-medium px-2 py-0.5 rounded-full ${mentionRateColor(
                response.mention_rate
              )}`}
            >
              {mentionLabel}
            </span>
          )}
        </div>
      </div>

      {/* Representative response body */}
      <div className="flex-1 px-4 py-3 overflow-y-auto max-h-64">
        {response.error && !response.response_text ? (
          <p className="text-sm text-red-600 italic">{response.error}</p>
        ) : (
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {response.response_text || <span className="italic text-gray-400">No response</span>}
          </p>
        )}
      </div>

      {/* Variations toggle */}
      {totalVariations > 0 && (
        <div className="border-t border-gray-100">
          <button
            onClick={() => setShowVariations((v) => !v)}
            className="w-full flex items-center justify-between px-4 py-2 text-xs text-gray-500 hover:bg-gray-50 transition-colors"
          >
            <span>
              {totalVariations} prompt variation{totalVariations !== 1 ? "s" : ""}
            </span>
            <svg
              className={`w-4 h-4 transition-transform ${showVariations ? "rotate-180" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showVariations && (
            <div className="divide-y divide-gray-100">
              {response.variation_responses.map((v, i) => (
                <div key={i} className="px-4 py-3 bg-gray-50">
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <p className="text-xs font-medium text-gray-500">
                      Prompt {i + 1}
                    </p>
                    <span
                      className={`shrink-0 text-xs font-medium px-1.5 py-0.5 rounded-full ${
                        v.error
                          ? "bg-red-100 text-red-600"
                          : v.brand_mentioned
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-500"
                      }`}
                    >
                      {v.error ? "Error" : v.brand_mentioned ? "Mentioned" : "Not mentioned"}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 italic mb-2">"{v.prompt}"</p>
                  {v.error ? (
                    <p className="text-xs text-red-500">{v.error}</p>
                  ) : (
                    <p className="text-xs text-gray-600 whitespace-pre-wrap leading-relaxed line-clamp-6">
                      {v.response_text}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
