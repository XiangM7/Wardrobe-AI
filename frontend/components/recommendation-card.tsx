"use client";

import { useState } from "react";

import type { OutfitRecommendation } from "@/lib/types";
import { buildImageUrl, titleCase } from "@/lib/utils";

type RecommendationCardProps = {
  recommendation: OutfitRecommendation;
  onFeedbackSubmit?: (outfitId: number, payload: { liked: boolean; saved: boolean; worn: boolean; feedbackText: string }) => Promise<void>;
};

const scoreLabels: Array<{
  key:
    | "compatibility_score"
    | "user_fit_score"
    | "style_match_score"
    | "scene_match_score"
    | "weather_match_score"
    | "preference_score"
    | "repetition_penalty";
  label: string;
}> = [
  { key: "compatibility_score", label: "Compatibility" },
  { key: "user_fit_score", label: "User fit" },
  { key: "style_match_score", label: "Style match" },
  { key: "scene_match_score", label: "Scene match" },
  { key: "weather_match_score", label: "Weather" },
  { key: "preference_score", label: "Preference" },
  { key: "repetition_penalty", label: "Repeat penalty" },
];

export function RecommendationCard({
  recommendation,
  onFeedbackSubmit,
}: RecommendationCardProps) {
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const [worn, setWorn] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const items = [
    recommendation.top_item,
    recommendation.pants_item,
    recommendation.shoes_item,
  ];

  const handleFeedback = async () => {
    if (!onFeedbackSubmit) {
      return;
    }

    setSubmitting(true);
    try {
      await onFeedbackSubmit(recommendation.id, { liked, saved, worn, feedbackText });
      setFeedbackText("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <article className="panel overflow-hidden">
      <div className="border-b border-line bg-white/60 px-5 py-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <span className="eyebrow">Top Pick #{recommendation.id}</span>
            <h3 className="mt-4 font-display text-3xl text-ink">
              Score {recommendation.total_score.toFixed(1)}
            </h3>
            <p className="mt-2 max-w-2xl text-sm leading-7 text-muted">
              {recommendation.reason_text}
            </p>
          </div>
          <div className="rounded-[22px] bg-[rgba(217,231,223,0.7)] px-4 py-3 text-sm text-ink">
            Generated {new Date(recommendation.created_at).toLocaleString()}
          </div>
        </div>
      </div>

      <div className="grid gap-5 p-5 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="grid gap-4 md:grid-cols-3">
          {items.map((item) => (
            <div key={item.id} className="panel-muted overflow-hidden">
              <img
                src={buildImageUrl(item.image_path)}
                alt={`${item.category} item`}
                className="h-44 w-full object-cover"
              />
              <div className="space-y-2 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">
                  {titleCase(item.category)}
                </p>
                <h4 className="font-semibold text-ink">{item.brand || "Closet item"}</h4>
                <p className="text-sm text-muted">
                  {[item.primary_color, item.formality, item.fit].filter(Boolean).join(" • ") || "Metadata pending"}
                </p>
                <p className="text-xs text-muted">{item.style_tags.join(", ") || "No style tags"}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-5">
          <div className="panel-muted p-4">
            <h4 className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">
              Score breakdown
            </h4>
            <div className="mt-4 space-y-3">
              {scoreLabels.map((scoreLabel) => (
                <div key={scoreLabel.key}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span>{scoreLabel.label}</span>
                    <span className="font-semibold text-ink">
                      {recommendation[scoreLabel.key].toFixed(1)}
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-sand">
                    <div
                      className={`h-2 rounded-full ${
                        scoreLabel.key === "repetition_penalty" ? "bg-ink" : "bg-accent"
                      }`}
                      style={{
                        width: `${Math.min(100, recommendation[scoreLabel.key])}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {onFeedbackSubmit ? (
            <div className="panel-muted p-4">
              <h4 className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">
                Quick feedback
              </h4>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <label className="flex items-center gap-3 rounded-2xl border border-line bg-white px-4 py-3 text-sm">
                  <input type="checkbox" checked={liked} onChange={(event) => setLiked(event.target.checked)} />
                  Liked
                </label>
                <label className="flex items-center gap-3 rounded-2xl border border-line bg-white px-4 py-3 text-sm">
                  <input type="checkbox" checked={saved} onChange={(event) => setSaved(event.target.checked)} />
                  Saved
                </label>
                <label className="flex items-center gap-3 rounded-2xl border border-line bg-white px-4 py-3 text-sm">
                  <input type="checkbox" checked={worn} onChange={(event) => setWorn(event.target.checked)} />
                  Worn
                </label>
              </div>
              <textarea
                className="field-input mt-3 min-h-28"
                placeholder="What worked or felt off?"
                value={feedbackText}
                onChange={(event) => setFeedbackText(event.target.value)}
              />
              <button
                type="button"
                className="primary-button mt-4"
                onClick={handleFeedback}
                disabled={submitting}
              >
                {submitting ? "Sending..." : "Submit feedback"}
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </article>
  );
}
