import { VisibilityScore as VisibilityScoreType } from "@/lib/types";
import { PLATFORM_CONFIG } from "@/lib/constants";
import { LLMPlatform } from "@/lib/types";

interface Props {
  score: VisibilityScoreType;
}

function overallColor(rate: number): string {
  if (rate >= 0.8) return "text-green-600";
  if (rate >= 0.4) return "text-yellow-600";
  return "text-red-600";
}

function barColor(rate: number): string {
  if (rate >= 0.8) return "bg-green-500";
  if (rate >= 0.4) return "bg-yellow-500";
  return "bg-red-500";
}

function rateLabel(rate: number, total = 5): string {
  const count = Math.round(rate * total);
  const pct = Math.round(rate * 100);
  return `${count}/${total} (${pct}%)`;
}

export default function VisibilityScore({ score }: Props) {
  const overallPct = Math.round(score.overall_mention_rate * 100);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Visibility Score</h2>

      {/* Big number: platforms + avg rate */}
      <div className="flex items-end gap-3 mb-1">
        <span className={`text-5xl font-bold ${overallColor(score.overall_mention_rate)}`}>
          {score.score}
        </span>
        <div className="mb-1">
          <div className="text-2xl text-gray-400">/ 4 platforms</div>
          <div className={`text-sm font-semibold ${overallColor(score.overall_mention_rate)}`}>
            {overallPct}% avg mention rate
          </div>
        </div>
      </div>

      {/* Overall progress bar */}
      <div className="w-full bg-gray-100 rounded-full h-2.5 mb-5">
        <div
          className={`h-2.5 rounded-full transition-all ${barColor(score.overall_mention_rate)}`}
          style={{ width: `${overallPct}%` }}
        />
      </div>

      {/* Per-platform rows */}
      <div className="space-y-3">
        {(["chatgpt", "gemini", "claude", "rufus"] as LLMPlatform[]).map((platform) => {
          const rate = score.platform_rates[platform] ?? 0;
          const pct = Math.round(rate * 100);
          const config = PLATFORM_CONFIG[platform];
          return (
            <div key={platform}>
              <div className="flex items-center gap-2 mb-1">
                <div
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: config.color }}
                />
                <span className="text-sm text-gray-700 flex-1">{config.label}</span>
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    rate >= 0.8
                      ? "bg-green-100 text-green-700"
                      : rate >= 0.4
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-gray-100 text-gray-500"
                  }`}
                >
                  {rateLabel(rate)}
                </span>
              </div>
              {/* Mini progress bar per platform */}
              <div className="w-full bg-gray-100 rounded-full h-1.5 ml-4">
                <div
                  className={`h-1.5 rounded-full transition-all ${barColor(rate)}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
