"use client";

import { useEffect, useMemo, useState } from "react";

import { ClothingItemCard } from "@/components/clothing-item-card";
import { EmptyUserState } from "@/components/empty-user-state";
import { createClothingItem, deleteClothingItem, getClothingItems, updateClothingItem } from "@/lib/api";
import { CATEGORY_OPTIONS, FIT_OPTIONS, FORMALITY_OPTIONS, SEASON_SUGGESTIONS } from "@/lib/constants";
import { extractClothingMetadata } from "@/lib/metadata-extractor";
import { useCurrentUserId } from "@/lib/use-current-user";
import { csvToArray } from "@/lib/utils";
import type { ClothingFormValues, ClothingItem, ClothingUpdatePayload } from "@/lib/types";

const initialFormState: ClothingFormValues = {
  image: null,
  category: "tops",
  primary_color: "",
  secondary_color: "",
  style_tags: [],
  season_tags: [],
  formality: "casual",
  fit: "regular",
  brand: "",
  is_favorite: false,
  last_worn_date: "",
};

export default function ClosetPage() {
  const currentUserId = useCurrentUserId();
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [styleTagsInput, setStyleTagsInput] = useState("");
  const [seasonTagsInput, setSeasonTagsInput] = useState("");
  const [form, setForm] = useState<ClothingFormValues>(initialFormState);
  const [isAnalyzingImage, setIsAnalyzingImage] = useState(false);
  const [autoFillSummary, setAutoFillSummary] = useState("");

  useEffect(() => {
    async function loadCloset() {
      if (!currentUserId) {
        setItems([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const fetchedItems = await getClothingItems(currentUserId);
        setItems(fetchedItems);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load closet items.");
      } finally {
        setLoading(false);
      }
    }

    loadCloset();
  }, [currentUserId]);

  const categoryCounts = useMemo(() => {
    return CATEGORY_OPTIONS.reduce<Record<string, number>>((accumulator, category) => {
      accumulator[category] = items.filter((item) => item.category === category).length;
      return accumulator;
    }, {});
  }, [items]);

  const refreshCloset = async () => {
    if (!currentUserId) {
      return;
    }
    const fetchedItems = await getClothingItems(currentUserId);
    setItems(fetchedItems);
  };

  const handleCreate = async () => {
    if (!currentUserId) {
      return;
    }

    setError("");
    setStatus("");
    setSubmitting(true);

    try {
      await createClothingItem(currentUserId, {
        ...form,
        style_tags: csvToArray(styleTagsInput),
        season_tags: csvToArray(seasonTagsInput),
      });
      setForm(initialFormState);
      setStyleTagsInput("");
      setSeasonTagsInput("");
      setAutoFillSummary("");
      await refreshCloset();
      setStatus("Closet item uploaded and saved.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to add closet item.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAutoFillFromImage = async (selectedFile: File) => {
    setIsAnalyzingImage(true);
    setError("");

    try {
      const metadata = await extractClothingMetadata(selectedFile, form.category);
      setForm((current) => ({
        ...current,
        image: selectedFile,
        primary_color: current.primary_color || metadata.primaryColor,
        secondary_color: current.secondary_color || metadata.secondaryColor,
        formality:
          current.formality && current.formality !== initialFormState.formality
            ? current.formality
            : metadata.formality,
        fit:
          current.fit && current.fit !== initialFormState.fit
            ? current.fit
            : metadata.fit,
      }));
      setStyleTagsInput((current) => current || metadata.styleTags.join(", "));
      setSeasonTagsInput((current) => current || metadata.seasonTags.join(", "));
      setAutoFillSummary(
        `Auto-filled ${metadata.primaryColor}${metadata.secondaryColor ? ` + ${metadata.secondaryColor}` : ""}, ${metadata.styleTags.join(", ")}, ${metadata.seasonTags.join(", ")}.`,
      );
    } catch (analysisError) {
      setError(
        analysisError instanceof Error
          ? analysisError.message
          : "Unable to analyze the selected image.",
      );
    } finally {
      setIsAnalyzingImage(false);
    }
  };

  const handleSave = async (itemId: number, payload: ClothingUpdatePayload) => {
    setError("");
    setStatus("");
    try {
      const updatedItem = await updateClothingItem(itemId, payload);
      setItems((current) => current.map((item) => (item.id === updatedItem.id ? updatedItem : item)));
      setStatus("Item metadata updated.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Unable to update the clothing item.");
    }
  };

  const handleDelete = async (itemId: number) => {
    setError("");
    setStatus("");
    try {
      await deleteClothingItem(itemId);
      setItems((current) => current.filter((item) => item.id !== itemId));
      setStatus("Item removed from the closet.");
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Unable to delete the clothing item.");
    }
  };

  if (!currentUserId) {
    return (
      <div className="page-wrap py-10">
        <EmptyUserState
          title="Create a profile before building the closet."
          description="The closet is tied to a local user profile. Finish onboarding first, then upload tops, pants, and shoes here."
        />
      </div>
    );
  }

  return (
    <div className="page-wrap space-y-8 py-10">
      <section className="panel p-6 sm:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="eyebrow">Closet</span>
            <h1 className="mt-5 font-display text-5xl text-ink">Upload the pieces you actually wear.</h1>
            <p className="mt-4 max-w-3xl text-base leading-8 text-muted">
              For the MVP, every item needs to be one of three categories: tops, pants, or shoes. After upload, you can edit the metadata at any time.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {CATEGORY_OPTIONS.map((category) => (
              <div key={category} className="panel-muted p-4 text-center">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">{category}</p>
                <p className="mt-3 font-display text-3xl text-ink">{categoryCounts[category]}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="panel p-6 sm:p-8">
        <h2 className="section-title">Add clothing item</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="xl:col-span-2">
            <span className="field-label">Item image</span>
            <input
              type="file"
              accept="image/*"
              className="field-input"
              onChange={async (event) => {
                const selectedFile = event.target.files?.[0] || null;
                setForm((current) => ({ ...current, image: selectedFile }));
                if (selectedFile) {
                  await handleAutoFillFromImage(selectedFile);
                }
              }}
            />
          </label>

          <label>
            <span className="field-label">Category</span>
            <select
              className="field-input"
              value={form.category}
              onChange={(event) => setForm((current) => ({ ...current, category: event.target.value }))}
            >
              {CATEGORY_OPTIONS.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span className="field-label">Brand</span>
            <input
              className="field-input"
              placeholder="Uniqlo"
              value={form.brand}
              onChange={(event) => setForm((current) => ({ ...current, brand: event.target.value }))}
            />
          </label>

          <label>
            <span className="field-label">Primary color</span>
            <input
              className="field-input"
              placeholder="white"
              value={form.primary_color}
              onChange={(event) =>
                setForm((current) => ({ ...current, primary_color: event.target.value }))
              }
            />
          </label>

          <label>
            <span className="field-label">Secondary color</span>
            <input
              className="field-input"
              placeholder="navy"
              value={form.secondary_color}
              onChange={(event) =>
                setForm((current) => ({ ...current, secondary_color: event.target.value }))
              }
            />
          </label>

          <label>
            <span className="field-label">Formality</span>
            <select
              className="field-input"
              value={form.formality}
              onChange={(event) => setForm((current) => ({ ...current, formality: event.target.value }))}
            >
              {FORMALITY_OPTIONS.map((formality) => (
                <option key={formality} value={formality}>
                  {formality}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span className="field-label">Fit</span>
            <select
              className="field-input"
              value={form.fit}
              onChange={(event) => setForm((current) => ({ ...current, fit: event.target.value }))}
            >
              {FIT_OPTIONS.map((fit) => (
                <option key={fit} value={fit}>
                  {fit}
                </option>
              ))}
            </select>
          </label>

          <label className="md:col-span-2">
            <span className="field-label">Style tags</span>
            <input
              className="field-input"
              placeholder="clean, casual, minimal"
              value={styleTagsInput}
              onChange={(event) => setStyleTagsInput(event.target.value)}
            />
          </label>

          <label className="md:col-span-2">
            <span className="field-label">Season tags</span>
            <input
              className="field-input"
              placeholder={SEASON_SUGGESTIONS.join(", ")}
              value={seasonTagsInput}
              onChange={(event) => setSeasonTagsInput(event.target.value)}
            />
          </label>

          <label>
            <span className="field-label">Last worn date</span>
            <input
              type="date"
              className="field-input"
              value={form.last_worn_date}
              onChange={(event) =>
                setForm((current) => ({ ...current, last_worn_date: event.target.value }))
              }
            />
          </label>

          <label>
            <span className="field-label">Favorite</span>
            <div className="flex h-[52px] items-center rounded-2xl border border-line bg-white/80 px-4">
              <input
                type="checkbox"
                checked={form.is_favorite}
                onChange={(event) =>
                  setForm((current) => ({ ...current, is_favorite: event.target.checked }))
                }
              />
              <span className="ml-3 text-sm text-muted">Boost this piece in recommendations</span>
            </div>
          </label>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            className="primary-button"
            onClick={handleCreate}
            disabled={submitting || !form.image}
          >
            {submitting ? "Uploading..." : "Upload item"}
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={() => form.image && handleAutoFillFromImage(form.image)}
            disabled={!form.image || isAnalyzingImage}
          >
            {isAnalyzingImage ? "Analyzing..." : "Re-analyze image"}
          </button>
          {status ? <div className="status-pill">{status}</div> : null}
          {autoFillSummary ? <div className="status-pill">{autoFillSummary}</div> : null}
          {error ? <div className="rounded-full bg-[#f7d7d7] px-4 py-2 text-sm text-[#8a1f1f]">{error}</div> : null}
        </div>
        <p className="mt-4 text-sm text-muted">
          Uploading an image now auto-fills color, style tags, season tags, and a suggested formality. You can edit everything before saving.
        </p>
      </section>

      <section className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="section-title">Current closet</h2>
          <p className="text-sm text-muted">{items.length} total items</p>
        </div>

        {loading ? (
          <div className="panel p-8 text-sm text-muted">Loading closet items...</div>
        ) : items.length === 0 ? (
          <div className="panel p-8 text-sm text-muted">
            No items yet. Upload at least one top, one pair of pants, and one pair of shoes to unlock recommendations.
          </div>
        ) : (
          <div className="space-y-5">
            {items.map((item) => (
              <ClothingItemCard key={item.id} item={item} onSave={handleSave} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
