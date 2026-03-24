import { LLMResponse } from "@/lib/types";
import AIResponseCard from "./AIResponseCard";

interface Props {
  responses: LLMResponse[];
}

export default function AIResponseGrid({ responses }: Props) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-3">AI Responses</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {responses.map((r) => (
          <AIResponseCard key={r.platform} response={r} />
        ))}
      </div>
    </div>
  );
}
