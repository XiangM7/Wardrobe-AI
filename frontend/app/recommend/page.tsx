"use client";

import { useState } from "react";

import { EmptyUserState } from "@/components/empty-user-state";
import { RecommendationCard } from "@/components/recommendation-card";
import { createRecommendation, submitFeedback } from "@/lib/api";
import { SCENE_OPTIONS, STYLE_OPTIONS, WEATHER_OPTIONS } from "@/lib/constants";
import { useCurrentUserId } from "@/lib/use-current-user";
import type { RecommendationBundle } from "@/lib/types";

export default function RecommendPage() {
  const currentUserId = useCurrentUserId();
  const [targetStyle, setTargetStyle] = useState("clean");
  const [targetScene, setTargetScene] = useState("school");
  const [weather, setWeather] = useState("mild");
  const [extraNote, setExtraNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [bundle, setBundle] = useState<RecommendationBundle | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!currentUserId) {
      return;
    }

    setLoading(true);
    setError("");
    setStatus("");

    try {
      const nextBundle = await createRecommendation(currentUserId, {
        target_style: targetStyle,
        target_scene: targetScene,
        weather,
        extra_note: extraNote,
      });
      setBundle(nextBundle);
      setStatus("Three outfit recommendations are ready.");
    } catch (recommendationError) {
      setError(
        recommendationError instanceof Error
          ? recommendationError.message
          : "Unable to generate recommendations right now.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async (
    outfitId: number,
    payload: { liked: boolean; saved: boolean; worn: boolean; feedbackText: string },
  ) => {
    if (!currentUserId) {
      return;
    }

    try {
      await submitFeedback(currentUserId, {
        outfit_id: outfitId,
        liked: payload.liked,
        saved: payload.saved,
        worn: payload.worn,
        feedback_text: payload.feedbackText,
      });
      setStatus("Feedback saved for this recommendation.");
    } catch (feedbackError) {
      setError(feedbackError instanceof Error ? feedbackError.message : "Unable to submit feedback.");
    }
  };

  if (!currentUserId) {
    return (
      <div className="page-wrap py-10">
        <EmptyUserState
          title="Create a profile before requesting outfits."
          description="Recommendations use your local profile, closet items, and manual metadata. Finish onboarding and upload a full closet first."
        />
      </div>
    );
  }

  return (
    <div className="page-wrap space-y-8 py-10">
      <section className="panel p-6 sm:p-8">
        <span className="eyebrow">Today Outfit</span>
        <h1 className="mt-5 font-display text-5xl text-ink">Generate outfit picks for today.</h1>
        <p className="mt-4 max-w-3xl text-base leading-8 text-muted">
          The MVP ranks every valid top, pants, and shoes combination with deterministic scoring. No black-box model is involved.
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label>
            <span className="field-label">Target style</span>
            <select className="field-input" value={targetStyle} onChange={(event) => setTargetStyle(event.target.value)}>
              {STYLE_OPTIONS.map((style) => (
                <option key={style} value={style}>
                  {style}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span className="field-label">Target scene</span>
            <select className="field-input" value={targetScene} onChange={(event) => setTargetScene(event.target.value)}>
              {SCENE_OPTIONS.map((scene) => (
                <option key={scene} value={scene}>
                  {scene}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span className="field-label">Weather</span>
            <select className="field-input" value={weather} onChange={(event) => setWeather(event.target.value)}>
              {WEATHER_OPTIONS.map((weatherOption) => (
                <option key={weatherOption} value={weatherOption}>
                  {weatherOption}
                </option>
              ))}
            </select>
          </label>

          <label className="md:col-span-2 xl:col-span-1">
            <span className="field-label">Optional note</span>
            <input
              className="field-input"
              placeholder="Need to walk a lot today"
              value={extraNote}
              onChange={(event) => setExtraNote(event.target.value)}
            />
          </label>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button type="button" className="primary-button" onClick={handleSubmit} disabled={loading}>
            {loading ? "Scoring outfits..." : "Generate recommendations"}
          </button>
          {status ? <div className="status-pill">{status}</div> : null}
          {error ? <div className="rounded-full bg-[#f7d7d7] px-4 py-2 text-sm text-[#8a1f1f]">{error}</div> : null}
        </div>
      </section>

      {bundle ? (
        <section className="space-y-5">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="section-title">Recommendation set</h2>
              <p className="mt-2 text-sm text-muted">
                Request created {new Date(bundle.request.created_at).toLocaleString()} for {bundle.request.target_scene} in{" "}
                {bundle.request.weather} weather.
              </p>
            </div>
          </div>

          <div className="space-y-5">
            {bundle.recommendations.map((recommendation) => (
              <RecommendationCard
                key={recommendation.id}
                recommendation={recommendation}
                onFeedbackSubmit={handleFeedbackSubmit}
              />
            ))}
          </div>
        </section>
      ) : (
        <section className="panel p-8 text-sm leading-7 text-muted">
          Once your closet includes at least one top, one pair of pants, and one pair of shoes, this page will return your top three outfit combinations.
        </section>
      )}
    </div>
  );
}
