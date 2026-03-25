"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";

import { createUser, getProfile, getUser, seedDemoCloset, updateUser, upsertProfile } from "@/lib/api";
import { GOAL_OPTIONS, STYLE_OPTIONS } from "@/lib/constants";
import { clearStoredUserId, setStoredUserId, useCurrentUserId } from "@/lib/use-current-user";
import { buildImageUrl, csvToArray } from "@/lib/utils";
import type { User, UserProfile } from "@/lib/types";

function toggleValue(values: string[], nextValue: string): string[] {
  return values.includes(nextValue)
    ? values.filter((value) => value !== nextValue)
    : [...values, nextValue];
}

export default function OnboardingPage() {
  const currentUserId = useCurrentUserId();
  const [activeUser, setActiveUser] = useState<User | null>(null);
  const [existingProfile, setExistingProfile] = useState<UserProfile | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [stylePreferences, setStylePreferences] = useState<string[]>([]);
  const [bodyGoals, setBodyGoals] = useState<string[]>([]);
  const [colorPreferences, setColorPreferences] = useState("");
  const [avoidTags, setAvoidTags] = useState("");
  const [notes, setNotes] = useState("");
  const [fullBodyImage, setFullBodyImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingDemo, setIsLoadingDemo] = useState(false);

  const resetDraft = () => {
    setActiveUser(null);
    setExistingProfile(null);
    setName("");
    setEmail("");
    setStylePreferences([]);
    setBodyGoals([]);
    setColorPreferences("");
    setAvoidTags("");
    setNotes("");
    setFullBodyImage(null);
    setPreviewUrl("");
  };

  useEffect(() => {
    let cancelled = false;

    async function hydrateExistingProfile() {
      if (!currentUserId) {
        if (!cancelled) {
          resetDraft();
        }
        return;
      }

      try {
        const user = await getUser(currentUserId);
        if (cancelled) {
          return;
        }

        setActiveUser(user);
        setName(user.name);
        setEmail(user.email);

        try {
          const profile = await getProfile(currentUserId);
          if (cancelled) {
            return;
          }
          setExistingProfile(profile);
          setStylePreferences(profile.style_preferences);
          setBodyGoals(profile.body_goals);
          setColorPreferences(profile.color_preferences.join(", "));
          setAvoidTags(profile.avoid_tags.join(", "));
          setNotes(profile.notes || "");
          setPreviewUrl(buildImageUrl(profile.full_body_image_path));
        } catch {
          if (!cancelled) {
            setExistingProfile(null);
          }
        }
      } catch {
        if (!cancelled) {
          setActiveUser(null);
          setExistingProfile(null);
        }
      }
    }

    hydrateExistingProfile();

    return () => {
      cancelled = true;
    };
  }, [currentUserId]);

  const helperCopy = useMemo(() => {
    if (!activeUser) {
      return "Create a local user, then save profile preferences and one full-body image.";
    }

    return "This local user already exists, so submitting will refresh the profile and preferences.";
  }, [activeUser]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0] || null;
    setFullBodyImage(nextFile);
    if (nextFile) {
      setPreviewUrl(URL.createObjectURL(nextFile));
    }
  };

  const handleSubmit = async () => {
    setError("");
    setStatus("");
    setIsSubmitting(true);

    try {
      const trimmedName = name.trim();
      const trimmedEmail = email.trim();
      if (!trimmedName || !trimmedEmail) {
        throw new Error("Name and email are required.");
      }

      const user = activeUser
        ? await updateUser(activeUser.id, {
            name: trimmedName,
            email: trimmedEmail,
          })
        : await createUser({
            name: trimmedName,
            email: trimmedEmail,
          });

      const formData = new FormData();
      formData.append("style_preferences", stylePreferences.join(", "));
      formData.append("body_goals", bodyGoals.join(", "));
      formData.append("color_preferences", colorPreferences);
      formData.append("avoid_tags", avoidTags);
      formData.append("notes", notes);
      if (fullBodyImage) {
        formData.append("full_body_image", fullBodyImage);
      }

      const profile = await upsertProfile(user.id, formData);
      setStoredUserId(user.id);
      setActiveUser(user);
      setExistingProfile(profile);
      setStatus(
        activeUser
          ? `Profile updated for ${user.name}.`
          : `Profile ready for ${user.name}. You can move on to the closet page now.`,
      );
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to save the onboarding flow.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateAnotherProfile = () => {
    clearStoredUserId();
    resetDraft();
    setStatus("Ready to create a new local profile.");
    setError("");
  };

  const handleLoadDemo = async () => {
    setIsLoadingDemo(true);
    setError("");
    setStatus("");

    try {
      const payload = await seedDemoCloset();
      setStoredUserId(payload.user.id);
      setStatus(`${payload.message} ${payload.clothing_count} items are ready for demo use.`);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load the demo closet.");
    } finally {
      setIsLoadingDemo(false);
    }
  };

  return (
    <div className="page-wrap space-y-8 py-10">
      <section className="panel overflow-hidden">
        <div className="grid gap-8 px-6 py-8 lg:grid-cols-[1.1fr_0.9fr] lg:px-10">
          <div>
            <span className="eyebrow">Onboarding</span>
            <h1 className="mt-5 font-display text-5xl text-ink">Build the personal styling baseline.</h1>
            <p className="mt-5 max-w-2xl text-base leading-8 text-muted">{helperCopy}</p>

            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <div className="panel-muted p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">Stored profile</p>
                <p className="mt-3 text-sm leading-7 text-ink">
                  {activeUser
                    ? `${activeUser.name} (${activeUser.email})`
                    : "No local profile selected yet."}
                </p>
              </div>
              <div className="panel-muted bg-[rgba(217,231,223,0.7)] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">One image</p>
                <p className="mt-3 text-sm leading-7 text-ink">
                  Upload a full-body image for styling context. Metadata editing stays manual in the MVP.
                </p>
              </div>
            </div>
          </div>

          <div className="panel-muted p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">Preview</p>
            <div className="mt-4 overflow-hidden rounded-[24px] border border-line bg-sand/40">
              {previewUrl ? (
                <img src={previewUrl} alt="Full body preview" className="h-[420px] w-full object-cover" />
              ) : (
                <div className="flex h-[420px] items-center justify-center px-8 text-center text-sm text-muted">
                  Full-body image preview appears here after upload or when a saved profile is loaded.
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="panel p-6 sm:p-8">
        <div className="grid gap-5 md:grid-cols-2">
          <label>
            <span className="field-label">Name</span>
            <input
              className="field-input"
              placeholder="Alex Kim"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </label>

          <label>
            <span className="field-label">Email</span>
            <input
              className="field-input"
              placeholder="alex@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          <label className="md:col-span-2">
            <span className="field-label">Full-body image</span>
            <input type="file" accept="image/*" className="field-input" onChange={handleFileChange} />
          </label>

          <div className="md:col-span-2">
            <span className="field-label">Style preferences</span>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
              {STYLE_OPTIONS.map((style) => (
                <label
                  key={style}
                  className={`rounded-2xl border px-4 py-4 text-sm transition ${
                    stylePreferences.includes(style)
                      ? "border-accent bg-white text-ink"
                      : "border-line bg-white/70 text-muted"
                  }`}
                >
                  <input
                    type="checkbox"
                    className="mr-3"
                    checked={stylePreferences.includes(style)}
                    onChange={() => setStylePreferences((current) => toggleValue(current, style))}
                  />
                  {style}
                </label>
              ))}
            </div>
          </div>

          <div className="md:col-span-2">
            <span className="field-label">Body goals</span>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {GOAL_OPTIONS.map((goal) => (
                <label
                  key={goal}
                  className={`rounded-2xl border px-4 py-4 text-sm transition ${
                    bodyGoals.includes(goal)
                      ? "border-accent bg-white text-ink"
                      : "border-line bg-white/70 text-muted"
                  }`}
                >
                  <input
                    type="checkbox"
                    className="mr-3"
                    checked={bodyGoals.includes(goal)}
                    onChange={() => setBodyGoals((current) => toggleValue(current, goal))}
                  />
                  {goal}
                </label>
              ))}
            </div>
          </div>

          <label>
            <span className="field-label">Color preferences</span>
            <input
              className="field-input"
              placeholder="white, navy, beige"
              value={colorPreferences}
              onChange={(event) => setColorPreferences(event.target.value)}
            />
          </label>

          <label>
            <span className="field-label">Avoid tags</span>
            <input
              className="field-input"
              placeholder="itchy, loud, tight"
              value={avoidTags}
              onChange={(event) => setAvoidTags(event.target.value)}
            />
          </label>

          <label className="md:col-span-2">
            <span className="field-label">Notes</span>
            <textarea
              className="field-input min-h-32"
              placeholder="Anything useful for recommendations, like favorite silhouettes or style boundaries."
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </label>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            className="primary-button"
            onClick={handleSubmit}
            disabled={
              isSubmitting ||
              !name.trim() ||
              !email.trim()
            }
          >
            {isSubmitting ? "Saving..." : activeUser ? "Save changes" : "Create profile"}
          </button>
          <button type="button" className="secondary-button" onClick={handleCreateAnotherProfile}>
            Start new local profile
          </button>
          <button type="button" className="secondary-button" onClick={handleLoadDemo} disabled={isLoadingDemo}>
            {isLoadingDemo ? "Loading demo..." : "Load demo closet"}
          </button>
          <div className="rounded-full border border-line px-4 py-3 text-sm text-muted">
            Color preferences saved as: {csvToArray(colorPreferences).join(", ") || "none"}
          </div>
        </div>

        {status ? <p className="mt-4 text-sm font-semibold text-[#1e5a4b]">{status}</p> : null}
        {error ? <p className="mt-4 text-sm font-semibold text-[#9e2a2b]">{error}</p> : null}
        {existingProfile ? (
          <p className="mt-4 text-sm text-muted">
            Existing profile last updated on {new Date(existingProfile.created_at).toLocaleString()}.
          </p>
        ) : null}
      </section>
    </div>
  );
}
