export type User = {
  id: number;
  name: string;
  email: string;
  created_at: string;
};

export type UserProfile = {
  id: number;
  user_id: number;
  full_body_image_path: string | null;
  style_preferences: string[];
  body_goals: string[];
  color_preferences: string[];
  avoid_tags: string[];
  notes: string | null;
  created_at: string;
};

export type ClothingItem = {
  id: number;
  user_id: number;
  image_path: string;
  category: string;
  primary_color: string | null;
  secondary_color: string | null;
  style_tags: string[];
  season_tags: string[];
  formality: string | null;
  fit: string | null;
  brand: string | null;
  is_favorite: boolean;
  last_worn_date: string | null;
  created_at: string;
};

export type RecommendationRequest = {
  id: number;
  user_id: number;
  target_style: string;
  target_scene: string;
  weather: string;
  extra_note: string | null;
  created_at: string;
};

export type OutfitRecommendation = {
  id: number;
  request_id: number;
  user_id: number;
  top_item_id: number;
  pants_item_id: number;
  shoes_item_id: number;
  total_score: number;
  compatibility_score: number;
  user_fit_score: number;
  style_match_score: number;
  scene_match_score: number;
  weather_match_score: number;
  preference_score: number;
  repetition_penalty: number;
  reason_text: string;
  created_at: string;
  top_item: ClothingItem;
  pants_item: ClothingItem;
  shoes_item: ClothingItem;
};

export type RecommendationBundle = {
  request: RecommendationRequest;
  recommendations: OutfitRecommendation[];
};

export type RecommendationHistoryEntry = {
  request: RecommendationRequest;
  recommendations: OutfitRecommendation[];
};

export type CreateUserPayload = {
  name: string;
  email: string;
};

export type ProfileFormValues = {
  style_preferences: string[];
  body_goals: string[];
  color_preferences: string[];
  avoid_tags: string[];
  notes: string;
  full_body_image?: File | null;
};

export type ClothingFormValues = {
  image?: File | null;
  category: string;
  primary_color: string;
  secondary_color: string;
  style_tags: string[];
  season_tags: string[];
  formality: string;
  fit: string;
  brand: string;
  is_favorite: boolean;
  last_worn_date: string;
};

export type ClothingUpdatePayload = {
  category?: string;
  primary_color?: string | null;
  secondary_color?: string | null;
  style_tags?: string[];
  season_tags?: string[];
  formality?: string | null;
  fit?: string | null;
  brand?: string | null;
  is_favorite?: boolean;
  last_worn_date?: string | null;
};

export type RecommendationRequestPayload = {
  target_style: string;
  target_scene: string;
  weather: string;
  extra_note?: string;
};

export type FeedbackPayload = {
  outfit_id: number;
  liked: boolean;
  saved: boolean;
  worn: boolean;
  feedback_text?: string;
};
