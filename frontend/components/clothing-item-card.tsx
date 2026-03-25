"use client";

import { useEffect, useState } from "react";

import type { ClothingItem, ClothingUpdatePayload } from "@/lib/types";
import { arrayToCsv, buildImageUrl, titleCase } from "@/lib/utils";

type ClothingItemCardProps = {
  item: ClothingItem;
  onSave: (itemId: number, payload: ClothingUpdatePayload) => Promise<void>;
  onDelete: (itemId: number) => Promise<void>;
};

type EditableState = {
  category: string;
  primary_color: string;
  secondary_color: string;
  style_tags: string;
  season_tags: string;
  formality: string;
  fit: string;
  brand: string;
  is_favorite: boolean;
  last_worn_date: string;
};

function toEditableState(item: ClothingItem): EditableState {
  return {
    category: item.category,
    primary_color: item.primary_color || "",
    secondary_color: item.secondary_color || "",
    style_tags: arrayToCsv(item.style_tags),
    season_tags: arrayToCsv(item.season_tags),
    formality: item.formality || "",
    fit: item.fit || "",
    brand: item.brand || "",
    is_favorite: item.is_favorite,
    last_worn_date: item.last_worn_date || "",
  };
}

export function ClothingItemCard({ item, onSave, onDelete }: ClothingItemCardProps) {
  const [form, setForm] = useState<EditableState>(() => toEditableState(item));
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    setForm(toEditableState(item));
  }, [item]);

  const handleSubmit = async () => {
    setSaving(true);
    try {
      await onSave(item.id, {
        category: form.category,
        primary_color: form.primary_color || null,
        secondary_color: form.secondary_color || null,
        style_tags: form.style_tags
          .split(",")
          .map((entry) => entry.trim())
          .filter(Boolean),
        season_tags: form.season_tags
          .split(",")
          .map((entry) => entry.trim())
          .filter(Boolean),
        formality: form.formality || null,
        fit: form.fit || null,
        brand: form.brand || null,
        is_favorite: form.is_favorite,
        last_worn_date: form.last_worn_date || null,
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Delete this item from the closet?")) {
      return;
    }

    setDeleting(true);
    try {
      await onDelete(item.id);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <article className="panel overflow-hidden">
      <div className="grid gap-0 lg:grid-cols-[220px_1fr]">
        <div className="border-b border-line bg-sand/40 lg:border-b-0 lg:border-r">
          <img
            src={buildImageUrl(item.image_path)}
            alt={`${item.category} item`}
            className="h-full min-h-[220px] w-full object-cover"
          />
        </div>

        <div className="space-y-5 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">
                {titleCase(item.category)}
              </p>
              <h3 className="mt-2 font-display text-2xl text-ink">
                {item.brand || "Closet piece"}
              </h3>
            </div>
            <div className="flex flex-wrap gap-2 text-xs text-muted">
              {item.is_favorite ? <span className="status-pill">Favorite</span> : null}
              <span className="rounded-full border border-line px-3 py-1">
                Created {new Date(item.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label>
              <span className="field-label">Category</span>
              <select
                className="field-input"
                value={form.category}
                onChange={(event) => setForm((current) => ({ ...current, category: event.target.value }))}
              >
                <option value="tops">Tops</option>
                <option value="pants">Pants</option>
                <option value="shoes">Shoes</option>
              </select>
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
                <span className="ml-3 text-sm text-muted">Boost this item in recommendations</span>
              </div>
            </label>

            <label>
              <span className="field-label">Primary color</span>
              <input
                className="field-input"
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
                value={form.secondary_color}
                onChange={(event) =>
                  setForm((current) => ({ ...current, secondary_color: event.target.value }))
                }
              />
            </label>

            <label>
              <span className="field-label">Style tags</span>
              <input
                className="field-input"
                value={form.style_tags}
                onChange={(event) => setForm((current) => ({ ...current, style_tags: event.target.value }))}
              />
            </label>

            <label>
              <span className="field-label">Season tags</span>
              <input
                className="field-input"
                value={form.season_tags}
                onChange={(event) => setForm((current) => ({ ...current, season_tags: event.target.value }))}
              />
            </label>

            <label>
              <span className="field-label">Formality</span>
              <input
                className="field-input"
                value={form.formality}
                onChange={(event) => setForm((current) => ({ ...current, formality: event.target.value }))}
              />
            </label>

            <label>
              <span className="field-label">Fit</span>
              <input
                className="field-input"
                value={form.fit}
                onChange={(event) => setForm((current) => ({ ...current, fit: event.target.value }))}
              />
            </label>

            <label>
              <span className="field-label">Brand</span>
              <input
                className="field-input"
                value={form.brand}
                onChange={(event) => setForm((current) => ({ ...current, brand: event.target.value }))}
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
          </div>

          <div className="flex flex-wrap gap-3">
            <button type="button" className="primary-button" onClick={handleSubmit} disabled={saving}>
              {saving ? "Saving..." : "Save metadata"}
            </button>
            <button type="button" className="secondary-button" onClick={handleDelete} disabled={deleting}>
              {deleting ? "Deleting..." : "Delete item"}
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
