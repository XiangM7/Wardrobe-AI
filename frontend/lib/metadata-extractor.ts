type ExtractedMetadata = {
  primaryColor: string;
  secondaryColor: string;
  styleTags: string[];
  seasonTags: string[];
  formality: string;
  fit: string;
};

type Category = "tops" | "pants" | "shoes";

type PaletteColor = {
  name: string;
  count: number;
};

const NEUTRAL_COLORS = new Set(["white", "black", "gray", "beige", "brown", "navy", "olive"]);

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function rgbToHsl(r: number, g: number, b: number) {
  const red = r / 255;
  const green = g / 255;
  const blue = b / 255;

  const max = Math.max(red, green, blue);
  const min = Math.min(red, green, blue);
  const delta = max - min;

  let hue = 0;
  if (delta !== 0) {
    if (max === red) {
      hue = ((green - blue) / delta) % 6;
    } else if (max === green) {
      hue = (blue - red) / delta + 2;
    } else {
      hue = (red - green) / delta + 4;
    }
    hue *= 60;
    if (hue < 0) {
      hue += 360;
    }
  }

  const lightness = (max + min) / 2;
  const saturation =
    delta === 0 ? 0 : delta / (1 - Math.abs(2 * lightness - 1));

  return { hue, saturation, lightness };
}

function guessColorName(r: number, g: number, b: number): string {
  const { hue, saturation, lightness } = rgbToHsl(r, g, b);

  if (lightness >= 0.86 && saturation <= 0.2) {
    return "white";
  }
  if (lightness <= 0.14) {
    return "black";
  }
  if (saturation <= 0.12) {
    return "gray";
  }
  if (hue >= 200 && hue <= 255 && lightness <= 0.4) {
    return "navy";
  }
  if (hue >= 35 && hue <= 55 && lightness >= 0.55 && saturation <= 0.45) {
    return "beige";
  }
  if (hue >= 20 && hue <= 42 && lightness <= 0.45) {
    return "brown";
  }
  if (hue >= 60 && hue <= 95 && lightness <= 0.45) {
    return "olive";
  }
  if (hue >= 0 && hue <= 15) {
    return "red";
  }
  if (hue > 15 && hue <= 40) {
    return "orange";
  }
  if (hue > 40 && hue <= 65) {
    return "yellow";
  }
  if (hue > 65 && hue <= 165) {
    return "green";
  }
  if (hue > 165 && hue <= 255) {
    return "blue";
  }
  if (hue > 255 && hue <= 320) {
    return "purple";
  }
  return "pink";
}

async function loadImage(file: File): Promise<HTMLImageElement> {
  const objectUrl = URL.createObjectURL(file);

  try {
    const image = await new Promise<HTMLImageElement>((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error("Unable to read the selected image."));
      image.src = objectUrl;
    });
    return image;
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}

function buildPalette(image: HTMLImageElement): {
  colors: PaletteColor[];
  averageSaturation: number;
  averageLightness: number;
} {
  const canvas = document.createElement("canvas");
  const maxSize = 64;
  const scale = Math.max(image.width, image.height) > maxSize ? maxSize / Math.max(image.width, image.height) : 1;
  canvas.width = Math.max(1, Math.round(image.width * scale));
  canvas.height = Math.max(1, Math.round(image.height * scale));

  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Canvas context is not available in this browser.");
  }

  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  const { data } = context.getImageData(0, 0, canvas.width, canvas.height);

  const counts = new Map<string, number>();
  let saturationTotal = 0;
  let lightnessTotal = 0;
  let sampled = 0;

  for (let index = 0; index < data.length; index += 16) {
    const alpha = data[index + 3];
    if (alpha < 140) {
      continue;
    }

    const red = data[index];
    const green = data[index + 1];
    const blue = data[index + 2];
    const colorName = guessColorName(red, green, blue);
    const { saturation, lightness } = rgbToHsl(red, green, blue);

    counts.set(colorName, (counts.get(colorName) || 0) + 1);
    saturationTotal += saturation;
    lightnessTotal += lightness;
    sampled += 1;
  }

  const colors = Array.from(counts.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((left, right) => right.count - left.count);

  return {
    colors,
    averageSaturation: sampled ? saturationTotal / sampled : 0,
    averageLightness: sampled ? lightnessTotal / sampled : 0.5,
  };
}

function inferStyleTags(category: Category, primaryColor: string, saturation: number): string[] {
  const tags = new Set<string>(["casual"]);
  if (category === "shoes") {
    tags.add("clean");
  }
  if (NEUTRAL_COLORS.has(primaryColor) || saturation < 0.22) {
    tags.add("clean");
    tags.add("minimal");
  }
  if (saturation > 0.45 && !NEUTRAL_COLORS.has(primaryColor)) {
    tags.add("street");
  }
  if (category === "pants" && NEUTRAL_COLORS.has(primaryColor)) {
    tags.add("smart-casual");
  }
  return Array.from(tags);
}

function inferSeasonTags(primaryColor: string, lightness: number): string[] {
  if (lightness >= 0.72) {
    return ["spring", "summer"];
  }
  if (lightness <= 0.34) {
    return ["autumn", "winter"];
  }
  if (primaryColor === "beige" || primaryColor === "white") {
    return ["spring", "summer", "autumn"];
  }
  return ["spring", "autumn", "winter"];
}

function inferFormality(category: Category, primaryColor: string, saturation: number): string {
  if (category === "shoes" && ["black", "brown", "navy"].includes(primaryColor)) {
    return "smart-casual";
  }
  if (category === "pants" && ["black", "navy", "brown"].includes(primaryColor) && saturation < 0.3) {
    return "smart-casual";
  }
  if (category === "tops" && NEUTRAL_COLORS.has(primaryColor) && saturation < 0.18) {
    return "smart-casual";
  }
  return "casual";
}

export async function extractClothingMetadata(
  file: File,
  category: string,
): Promise<ExtractedMetadata> {
  const normalizedCategory: Category =
    category === "pants" || category === "shoes" ? category : "tops";
  const image = await loadImage(file);
  const palette = buildPalette(image);

  const primaryColor = palette.colors[0]?.name || "white";
  const secondaryColor =
    palette.colors.find((entry) => entry.name !== primaryColor && entry.count >= 4)?.name || "";
  const styleTags = inferStyleTags(normalizedCategory, primaryColor, palette.averageSaturation);
  const seasonTags = inferSeasonTags(primaryColor, palette.averageLightness);
  const formality = inferFormality(normalizedCategory, primaryColor, palette.averageSaturation);

  return {
    primaryColor,
    secondaryColor,
    styleTags,
    seasonTags,
    formality,
    fit:
      normalizedCategory === "tops"
        ? "regular"
        : clamp(palette.averageLightness, 0, 1) > 0.5
          ? "regular"
          : "slim",
  };
}
