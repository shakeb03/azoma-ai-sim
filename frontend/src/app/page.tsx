"use client";

import SearchForm from "@/components/SearchForm";
import LoadingState from "@/components/LoadingState";
import ResultsDashboard from "@/components/ResultsDashboard";
import { useSimulation } from "@/hooks/useSimulation";

export default function Home() {
  const { state, run, reset } = useSimulation();

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-xl font-bold text-gray-900">
            AI Shopping Gap Analyzer
          </h1>
          <p className="text-sm text-gray-500">
            See what your brand says vs. what AI platforms tell shoppers
          </p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Search form always visible unless showing results */}
        {state.status !== "success" && (
          <div className="mb-8">
            <div className="text-center mb-6">
              <p className="text-gray-600 text-sm max-w-xl mx-auto">
                Paste any product page URL. We&apos;ll scrape the listing, generate
                natural shopping prompts, query ChatGPT, Gemini, Claude, and Rufus in
                parallel, then surface the gap between what the brand says and what AI
                tells shoppers.
              </p>
            </div>
            <SearchForm
              onSubmit={run}
              loading={state.status === "loading"}
            />
          </div>
        )}

        {/* Loading */}
        {state.status === "loading" && (
          <LoadingState stage={state.stage} />
        )}

        {/* Error */}
        {state.status === "error" && (
          <div className="max-w-2xl mx-auto mt-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="font-medium text-red-800 mb-1">
                Analysis failed{state.stage !== "unknown" ? ` at: ${state.stage}` : ""}
              </p>
              <p className="text-sm text-red-600">{state.message}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {state.status === "success" && (
          <ResultsDashboard data={state.data} onReset={reset} />
        )}
      </div>
    </main>
  );
}
