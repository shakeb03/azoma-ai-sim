import { LOADING_STAGES, LoadingStage } from "@/lib/constants";

interface Props {
  stage: LoadingStage;
}

export default function LoadingState({ stage }: Props) {
  const currentIndex = LOADING_STAGES.findIndex((s) => s.key === stage);

  return (
    <div className="flex flex-col items-center gap-6 py-16">
      <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      <div className="flex flex-col items-center gap-4 w-full max-w-sm">
        {LOADING_STAGES.map((s, i) => (
          <div key={s.key} className="flex items-center gap-3 w-full">
            <div
              className={`w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold ${
                i < currentIndex
                  ? "bg-blue-600 text-white"
                  : i === currentIndex
                  ? "bg-blue-600 text-white animate-pulse"
                  : "bg-gray-200 text-gray-400"
              }`}
            >
              {i < currentIndex ? "✓" : i + 1}
            </div>
            <span
              className={`text-sm ${
                i === currentIndex
                  ? "text-gray-900 font-medium"
                  : i < currentIndex
                  ? "text-gray-400 line-through"
                  : "text-gray-400"
              }`}
            >
              {s.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
