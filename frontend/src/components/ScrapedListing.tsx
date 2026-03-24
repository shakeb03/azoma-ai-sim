"use client";

import { useState } from "react";
import { ScrapedListing as ScrapedListingType } from "@/lib/types";

interface Props {
  listing: ScrapedListingType;
}

export default function ScrapedListing({ listing }: Props) {
  const [expanded, setExpanded] = useState(false);
  const hasSpecs = Object.keys(listing.specs).length > 0;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
      <div className="flex items-start justify-between gap-2 mb-3">
        <h2 className="text-lg font-semibold text-gray-900">Ground Truth Listing</h2>
        <a
          href={listing.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-blue-600 hover:underline truncate max-w-[180px]"
        >
          {new URL(listing.url).hostname}
        </a>
      </div>

      {/* Metadata chips */}
      <div className="flex flex-wrap gap-2 mb-3">
        {listing.brand && (
          <span className="text-xs font-medium bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
            {listing.brand}
          </span>
        )}
        {listing.category && (
          <span className="text-xs font-medium bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full capitalize">
            {listing.category}
          </span>
        )}
        {listing.price && (
          <span className="text-xs font-medium bg-green-50 text-green-700 px-2 py-0.5 rounded-full">
            {listing.price}
          </span>
        )}
      </div>

      <p className="font-medium text-gray-800 mb-2">{listing.title}</p>

      {listing.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-3">{listing.description}</p>
      )}

      {hasSpecs && (
        <div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs font-medium text-blue-600 hover:underline mb-2"
          >
            {expanded ? "Hide specs" : `Show ${Object.keys(listing.specs).length} specs`}
          </button>

          {expanded && (
            <table className="w-full text-xs border-collapse">
              <tbody>
                {Object.entries(listing.specs).map(([k, v]) => (
                  <tr key={k} className="border-t border-gray-100">
                    <td className="py-1 pr-3 font-medium text-gray-600 align-top w-2/5">{k}</td>
                    <td className="py-1 text-gray-800">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
