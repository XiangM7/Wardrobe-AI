"use client";

import { useEffect, useState } from "react";

import { EmptyUserState } from "@/components/empty-user-state";
import { RecommendationCard } from "@/components/recommendation-card";
import { getRecommendationHistory } from "@/lib/api";
import { useCurrentUserId } from "@/lib/use-current-user";
import type { RecommendationHistoryEntry } from "@/lib/types";

export default function HistoryPage() {
  const currentUserId = useCurrentUserId();
  const [history, setHistory] = useState<RecommendationHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      if (!currentUserId) {
        setHistory([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError("");

      try {
        const entries = await getRecommendationHistory(currentUserId);
        setHistory(entries);
      } catch (historyError) {
        setError(historyError instanceof Error ? historyError.message : "Unable to load recommendation history.");
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, [currentUserId]);

  if (!currentUserId) {
    return (
      <div className="page-wrap py-10">
        <EmptyUserState
          title="History appears after your first recommendation run."
          description="Create a local profile, upload closet items, then generate outfits from the Today Outfit page."
        />
      </div>
    );
  }

  return (
    <div className="page-wrap space-y-8 py-10">
      <section className="panel p-6 sm:p-8">
        <span className="eyebrow">History</span>
        <h1 className="mt-5 font-display text-5xl text-ink">See past outfit recommendation sets.</h1>
        <p className="mt-4 max-w-3xl text-base leading-8 text-muted">
          Every recommendation request is stored with the scoring breakdown and the exact top, pants, and shoes combination that was returned.
        </p>
      </section>

      {loading ? <section className="panel p-8 text-sm text-muted">Loading recommendation history...</section> : null}
      {error ? <section className="panel p-8 text-sm text-[#8a1f1f]">{error}</section> : null}

      {!loading && !error && history.length === 0 ? (
        <section className="panel p-8 text-sm leading-7 text-muted">
          No history yet. Generate your first recommendation bundle from the Today Outfit page.
        </section>
      ) : null}

      {!loading && !error && history.length > 0 ? (
        <div className="space-y-8">
          {history.map((entry) => (
            <section key={entry.request.id} className="space-y-5">
              <div className="panel p-6">
                <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
                  <div>
                    <span className="eyebrow">Request #{entry.request.id}</span>
                    <h2 className="mt-4 font-display text-3xl text-ink">
                      {entry.request.target_style} for {entry.request.target_scene}
                    </h2>
                    <p className="mt-3 text-sm leading-7 text-muted">
                      Weather: {entry.request.weather}
                      {entry.request.extra_note ? ` • Note: ${entry.request.extra_note}` : ""}
                    </p>
                  </div>
                  <div className="status-pill">
                    {new Date(entry.request.created_at).toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="space-y-5">
                {entry.recommendations.map((recommendation) => (
                  <RecommendationCard key={recommendation.id} recommendation={recommendation} />
                ))}
              </div>
            </section>
          ))}
        </div>
      ) : null}
    </div>
  );
}
