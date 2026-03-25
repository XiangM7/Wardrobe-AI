import { API_URL } from "@/lib/constants";

export function csvToArray(value: string): string[] {
  return value
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

export function arrayToCsv(values: string[]): string {
  return values.join(", ");
}

export function buildImageUrl(imagePath: string | null | undefined): string {
  if (!imagePath) {
    return "";
  }

  if (imagePath.startsWith("http://") || imagePath.startsWith("https://")) {
    return imagePath;
  }

  return `${API_URL}/${imagePath.replace(/^\//, "")}`;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) {
    return "Not set";
  }

  return new Date(value).toLocaleDateString();
}

export function titleCase(value: string): string {
  return value
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
