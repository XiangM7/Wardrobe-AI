export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export const CURRENT_USER_STORAGE_KEY = "wardrobe-ai-current-user-id";
export const USER_CHANGED_EVENT = "wardrobe-ai-user-changed";

export const STYLE_OPTIONS = ["clean", "casual", "minimal", "street", "smart-casual"];
export const GOAL_OPTIONS = ["look taller", "look slimmer", "look cleaner", "more comfortable"];
export const SCENE_OPTIONS = ["school", "work", "date", "outing"];
export const WEATHER_OPTIONS = ["cold", "mild", "hot"];
export const CATEGORY_OPTIONS = ["tops", "pants", "shoes"];
export const FORMALITY_OPTIONS = ["casual", "smart-casual", "formal"];
export const FIT_OPTIONS = ["slim", "regular", "relaxed", "oversized"];
export const SEASON_SUGGESTIONS = ["spring", "summer", "autumn", "winter"];
