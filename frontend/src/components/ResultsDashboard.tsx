import { SimulateResponse } from "@/lib/types";
import AIResponseGrid from "./AIResponseGrid";
import GapReportPanel from "./GapReportPanel";
import VisibilityScore from "./VisibilityScore";
import ScrapedListing from "./ScrapedListing";
import GeneratedPrompts from "./GeneratedPrompts";

interface Props {
  data: SimulateResponse;
  onReset: () => void;
}

export default function ResultsDashboard({ data, onReset }: Props) {
  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            {data.scraped_listing.brand
              ? `${data.scraped_listing.brand} — ${data.scraped_listing.category}`
              : data.scraped_listing.title}
          </h1>
          <p className="text-sm text-gray-500">
            Completed in {(data.duration_ms / 1000).toFixed(1)}s
          </p>
        </div>
        <button
          onClick={onReset}
          className="px-4 py-2 text-sm rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
        >
          New search
        </button>
      </div>

      {/* Top row: listing + score */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <ScrapedListing listing={data.scraped_listing} />
        </div>
        <div>
          <VisibilityScore score={data.visibility_score} />
        </div>
      </div>

      {/* Generated prompts */}
      <GeneratedPrompts prompts={data.generated_prompts} />

      {/* AI responses grid */}
      <AIResponseGrid responses={data.llm_responses} />

      {/* Gap report */}
      <GapReportPanel report={data.gap_report} />
    </div>
  );
}
