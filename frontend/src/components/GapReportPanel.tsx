import { GapReport } from "@/lib/types";

interface Props {
  report: GapReport;
}

function Check({ value }: { value: boolean }) {
  return value ? (
    <span className="text-green-600 font-bold">✓</span>
  ) : (
    <span className="text-red-400">✗</span>
  );
}

export default function GapReportPanel({ report }: Props) {
  const accuracy = Math.round(report.overall_accuracy_pct);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Gap Report</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Overall coverage</span>
          <span
            className={`text-sm font-bold px-2 py-0.5 rounded-full ${
              accuracy >= 75
                ? "bg-green-100 text-green-700"
                : accuracy >= 50
                ? "bg-yellow-100 text-yellow-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {accuracy}%
          </span>
        </div>
      </div>

      {/* Attribute coverage table */}
      {report.gap_fields.length > 0 && (
        <div className="overflow-x-auto mb-5">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 pr-3 text-gray-600 font-medium">Attribute</th>
                <th className="text-center py-2 px-2 text-gray-600 font-medium">Listed</th>
                <th className="text-center py-2 px-2 text-gray-600 font-medium">GPT</th>
                <th className="text-center py-2 px-2 text-gray-600 font-medium">Gemini</th>
                <th className="text-center py-2 px-2 text-gray-600 font-medium">Claude</th>
                <th className="text-center py-2 px-2 text-gray-600 font-medium">Rufus</th>
                <th className="text-left py-2 pl-3 text-gray-600 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody>
              {report.gap_fields.map((field, i) => (
                <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2 pr-3 font-medium text-gray-800">{field.attribute}</td>
                  <td className="text-center py-2 px-2">
                    <Check value={field.in_listing} />
                  </td>
                  <td className="text-center py-2 px-2">
                    <Check value={field.in_chatgpt} />
                  </td>
                  <td className="text-center py-2 px-2">
                    <Check value={field.in_gemini} />
                  </td>
                  <td className="text-center py-2 px-2">
                    <Check value={field.in_claude} />
                  </td>
                  <td className="text-center py-2 px-2">
                    <Check value={field.in_rufus} />
                  </td>
                  <td className="py-2 pl-3 text-xs text-gray-500 max-w-xs">
                    {field.ground_truth_value && (
                      <span className="text-gray-700 font-medium mr-1">
                        {field.ground_truth_value}
                      </span>
                    )}
                    {field.notes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Missing attributes */}
        {report.missing_attributes.length > 0 && (
          <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
            <p className="text-xs font-semibold text-yellow-800 mb-2 uppercase tracking-wide">
              Missing from all AIs ({report.missing_attributes.length})
            </p>
            <ul className="space-y-1">
              {report.missing_attributes.map((attr, i) => (
                <li key={i} className="text-xs text-yellow-700 flex items-start gap-1">
                  <span className="mt-0.5">•</span>
                  <span>{attr}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Hallucinations */}
        {report.hallucinations.length > 0 && (
          <div className="bg-red-50 rounded-lg p-3 border border-red-200">
            <p className="text-xs font-semibold text-red-800 mb-2 uppercase tracking-wide">
              Hallucinations ({report.hallucinations.length})
            </p>
            <ul className="space-y-1">
              {report.hallucinations.map((h, i) => (
                <li key={i} className="text-xs text-red-700 flex items-start gap-1">
                  <span className="mt-0.5">•</span>
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {report.missing_attributes.length === 0 && report.hallucinations.length === 0 && (
          <div className="col-span-2 bg-green-50 rounded-lg p-3 border border-green-200">
            <p className="text-xs text-green-700 font-medium">
              No missing attributes or hallucinations detected.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
