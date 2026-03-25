import { API_URL } from "@/lib/constants";
import type {
  ClothingFormValues,
  ClothingItem,
  ClothingUpdatePayload,
  CreateUserPayload,
  DemoSeedResponse,
  FeedbackPayload,
  RecommendationBundle,
  RecommendationHistoryEntry,
  RecommendationRequestPayload,
  User,
  UserProfile,
  UserUpdatePayload,
} from "@/lib/types";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = "Request failed.";

    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function createUser(payload: CreateUserPayload): Promise<User> {
  const response = await fetch(`${API_URL}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return parseResponse<User>(response);
}

export async function getUsers(): Promise<User[]> {
  const response = await fetch(`${API_URL}/users`, { cache: "no-store" });
  return parseResponse<User[]>(response);
}

export async function getUser(userId: number): Promise<User> {
  const response = await fetch(`${API_URL}/users/${userId}`, { cache: "no-store" });
  return parseResponse<User>(response);
}

export async function updateUser(userId: number, payload: UserUpdatePayload): Promise<User> {
  const response = await fetch(`${API_URL}/users/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return parseResponse<User>(response);
}

export async function upsertProfile(userId: number, values: FormData): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/profiles/${userId}`, {
    method: "POST",
    body: values,
  });

  return parseResponse<UserProfile>(response);
}

export async function getProfile(userId: number): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/profiles/${userId}`, { cache: "no-store" });
  return parseResponse<UserProfile>(response);
}

export async function createClothingItem(userId: number, values: ClothingFormValues): Promise<ClothingItem> {
  const formData = new FormData();
  if (values.image) {
    formData.append("image", values.image);
  }
  formData.append("category", values.category);
  formData.append("primary_color", values.primary_color);
  formData.append("secondary_color", values.secondary_color);
  formData.append("style_tags", values.style_tags.join(", "));
  formData.append("season_tags", values.season_tags.join(", "));
  formData.append("formality", values.formality);
  formData.append("fit", values.fit);
  formData.append("brand", values.brand);
  formData.append("is_favorite", String(values.is_favorite));
  formData.append("last_worn_date", values.last_worn_date);

  const response = await fetch(`${API_URL}/clothing/${userId}`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<ClothingItem>(response);
}

export async function getClothingItems(userId: number): Promise<ClothingItem[]> {
  const response = await fetch(`${API_URL}/clothing/${userId}`, { cache: "no-store" });
  return parseResponse<ClothingItem[]>(response);
}

export async function updateClothingItem(
  itemId: number,
  payload: ClothingUpdatePayload,
): Promise<ClothingItem> {
  const response = await fetch(`${API_URL}/clothing/item/${itemId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return parseResponse<ClothingItem>(response);
}

export async function deleteClothingItem(itemId: number): Promise<void> {
  const response = await fetch(`${API_URL}/clothing/item/${itemId}`, {
    method: "DELETE",
  });

  return parseResponse<void>(response);
}

export async function createRecommendation(
  userId: number,
  payload: RecommendationRequestPayload,
): Promise<RecommendationBundle> {
  const response = await fetch(`${API_URL}/recommend/${userId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return parseResponse<RecommendationBundle>(response);
}

export async function getRecommendationHistory(userId: number): Promise<RecommendationHistoryEntry[]> {
  const response = await fetch(`${API_URL}/recommend/history/${userId}`, { cache: "no-store" });
  return parseResponse<RecommendationHistoryEntry[]>(response);
}

export async function submitFeedback(userId: number, payload: FeedbackPayload) {
  const response = await fetch(`${API_URL}/feedback/${userId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return parseResponse(response);
}

export async function seedDemoCloset(): Promise<DemoSeedResponse> {
  const response = await fetch(`${API_URL}/demo/seed`, {
    method: "POST",
  });

  return parseResponse<DemoSeedResponse>(response);
}
