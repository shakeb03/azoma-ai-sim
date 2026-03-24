"use client";

import { useState } from "react";

interface Props {
  onSubmit: (url: string) => void;
  loading: boolean;
}

function isValidUrl(value: string): boolean {
  try {
    const u = new URL(value);
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
}

export default function SearchForm({ onSubmit, loading }: Props) {
  const [url, setUrl] = useState("");
  const valid = isValidUrl(url.trim());

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (valid) onSubmit(url.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste a product page URL — e.g. https://www.canadiantire.ca/en/..."
          disabled={loading}
          className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-400 disabled:opacity-50 disabled:bg-gray-50"
        />
        <button
          type="submit"
          disabled={loading || !valid}
          className="px-6 py-3 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>
      {url && !valid && (
        <p className="mt-2 text-xs text-red-500 pl-1">
          Please enter a valid http:// or https:// URL.
        </p>
      )}
    </form>
  );
}
