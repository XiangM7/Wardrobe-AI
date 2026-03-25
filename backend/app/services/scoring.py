from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from itertools import combinations

from app.models.clothing import ClothingItem
from app.models.profile import UserProfile
from app.models.recommendation import RecommendationRequest


NEUTRAL_COLORS = {"black", "white", "gray", "grey", "navy", "beige", "cream", "brown", "tan", "olive"}
FORMALITY_SCALE = {"casual": 1, "smart-casual": 2, "formal": 3}
WEATHER_TO_SEASONS = {
    "cold": {"winter", "autumn", "fall"},
    "mild": {"spring", "autumn", "fall"},
    "hot": {"summer", "spring"},
}
SCENE_PROFILES = {
    "school": {"styles": {"casual", "clean", "minimal", "street"}, "range": (1, 2)},
    "work": {"styles": {"clean", "minimal", "smart-casual"}, "range": (2, 3)},
    "date": {"styles": {"clean", "minimal", "smart-casual", "street"}, "range": (2, 3)},
    "outing": {"styles": {"casual", "street", "minimal", "clean"}, "range": (1, 2)},
}


@dataclass(slots=True)
class ScoreResult:
    compatibility_score: float
    user_fit_score: float
    style_match_score: float
    scene_match_score: float
    weather_match_score: float
    preference_score: float
    repetition_penalty: float
    total_score: float


def normalize_tag(value: str) -> str:
    return value.strip().lower().replace("_", "-")


def normalize_tags(values: list[str] | None) -> set[str]:
    if not values:
        return set()

    normalized: set[str] = set()
    for raw_value in values:
        cleaned = normalize_tag(raw_value)
        if not cleaned:
            continue
        normalized.add(cleaned)
        normalized.update(part for part in cleaned.replace("/", " ").replace("-", " ").split() if part)
    return normalized


def normalize_goals(values: list[str] | None) -> list[str]:
    if not values:
        return []

    canonical_goals: list[str] = []
    for raw_value in values:
        cleaned = normalize_tag(raw_value)
        if not cleaned:
            continue
        if "taller" in cleaned and "taller" not in canonical_goals:
            canonical_goals.append("taller")
        if "slimmer" in cleaned and "slimmer" not in canonical_goals:
            canonical_goals.append("slimmer")
        if "cleaner" in cleaned and "cleaner" not in canonical_goals:
            canonical_goals.append("cleaner")
        if "comfort" in cleaned and "comfortable" not in canonical_goals:
            canonical_goals.append("comfortable")
    return canonical_goals


def is_neutral_color(color: str | None) -> bool:
    return normalize_tag(color or "") in NEUTRAL_COLORS


def get_item_styles(item: ClothingItem) -> set[str]:
    return normalize_tags(item.style_tags)


def get_item_seasons(item: ClothingItem) -> set[str]:
    return normalize_tags(item.season_tags)


def formality_value(item: ClothingItem) -> int:
    return FORMALITY_SCALE.get(normalize_tag(item.formality or "casual"), 1)


def color_coordination_score(items: tuple[ClothingItem, ClothingItem, ClothingItem]) -> float:
    colors = [normalize_tag(item.primary_color or "") for item in items]
    colors = [color for color in colors if color]

    if not colors:
        return 58.0

    unique_colors = set(colors)
    neutral_count = sum(is_neutral_color(color) for color in colors)

    score = 42.0
    if neutral_count >= 2:
        score += 24.0
    if len(unique_colors) == 1:
        score += 20.0
    elif len(unique_colors) == 2:
        score += 14.0

    if len(colors) >= 2 and any(color in {"white", "cream", "beige"} for color in colors) and any(
        color in {"black", "navy", "brown", "olive"} for color in colors
    ):
        score += 12.0

    saturated = [color for color in unique_colors if color and not is_neutral_color(color)]
    if len(saturated) >= 3:
        score -= 12.0

    return clamp(score)


def style_consistency_score(items: tuple[ClothingItem, ClothingItem, ClothingItem], target_style: str) -> float:
    style_sets = [get_item_styles(item) for item in items]
    shared_pairs = sum(1 for left, right in combinations(style_sets, 2) if left & right)
    all_styles = set().union(*style_sets)
    target_tokens = normalize_tags([target_style])

    score = 38.0 + (shared_pairs * 18.0)
    if target_tokens & all_styles:
        score += 18.0
    if {"clean", "minimal"} & all_styles and {"street", "casual"} & all_styles:
        score += 6.0

    return clamp(score)


def formality_consistency_score(items: tuple[ClothingItem, ClothingItem, ClothingItem]) -> float:
    values = [formality_value(item) for item in items]
    spread = max(values) - min(values)
    if spread == 0:
        return 90.0
    if spread == 1:
        return 74.0
    return 44.0


def compatibility_score(items: tuple[ClothingItem, ClothingItem, ClothingItem], target_style: str) -> float:
    color_score = color_coordination_score(items)
    style_score = style_consistency_score(items, target_style)
    formal_score = formality_consistency_score(items)
    return clamp((0.38 * color_score) + (0.34 * style_score) + (0.28 * formal_score))


def style_match_score(items: tuple[ClothingItem, ClothingItem, ClothingItem], target_style: str) -> float:
    requested = normalize_tags([target_style])
    all_styles = set().union(*(get_item_styles(item) for item in items))

    if not requested:
        return 60.0

    overlap = len(requested & all_styles)
    ratio = overlap / max(len(requested), 1)
    base = 30.0 + (ratio * 60.0)

    if target_style.lower() in {"smart-casual", "clean casual"} and {"clean", "casual"} <= all_styles:
        base += 8.0

    return clamp(base)


def scene_match_score(items: tuple[ClothingItem, ClothingItem, ClothingItem], target_scene: str) -> float:
    scene = SCENE_PROFILES.get(normalize_tag(target_scene))
    if not scene:
        return 60.0

    styles = set().union(*(get_item_styles(item) for item in items))
    preferred_styles = scene["styles"]
    overlap = len(styles & preferred_styles)
    style_ratio = overlap / max(len(preferred_styles), 1)

    formalities = [formality_value(item) for item in items]
    average_formality = sum(formalities) / len(formalities)
    lower, upper = scene["range"]
    if lower <= average_formality <= upper:
        formality_score = 28.0
    else:
        distance = min(abs(average_formality - lower), abs(average_formality - upper))
        formality_score = max(8.0, 28.0 - (distance * 12.0))

    return clamp(32.0 + (style_ratio * 40.0) + formality_score)


def weather_match_score(items: tuple[ClothingItem, ClothingItem, ClothingItem], weather: str) -> float:
    target_seasons = WEATHER_TO_SEASONS.get(normalize_tag(weather))
    if not target_seasons:
        return 60.0

    item_scores: list[float] = []
    for item in items:
        seasons = get_item_seasons(item)
        if not seasons:
            item_scores.append(58.0)
        elif seasons & target_seasons:
            item_scores.append(85.0)
        else:
            item_scores.append(20.0)

    return clamp(sum(item_scores) / len(item_scores))


def user_fit_score(
    items: tuple[ClothingItem, ClothingItem, ClothingItem],
    profile: UserProfile | None,
    weather_score_value: float,
) -> float:
    normalized_goals = normalize_goals(profile.body_goals if profile else None)
    if not normalized_goals:
        return 62.0

    top, pants, shoes = items
    top_color = normalize_tag(top.primary_color or "")
    pants_color = normalize_tag(pants.primary_color or "")
    shoes_color = normalize_tag(shoes.primary_color or "")
    styles = set().union(*(get_item_styles(item) for item in items))
    fits = {normalize_tag(item.fit or "") for item in items}

    goal_scores: list[float] = []
    for goal in normalized_goals:
        score = 48.0
        if goal == "taller":
            if pants_color and shoes_color and pants_color == shoes_color:
                score += 18.0
            if top_color and pants_color and top_color == pants_color:
                score += 12.0
            if {"slim", "regular"} & fits:
                score += 10.0
        elif goal == "slimmer":
            if pants_color in {"black", "navy", "brown", "olive"}:
                score += 14.0
            if {"clean", "minimal"} & styles:
                score += 10.0
            if {"slim", "regular"} & fits:
                score += 8.0
        elif goal == "cleaner":
            if {"clean", "minimal", "smart-casual"} & styles:
                score += 18.0
            if sum(is_neutral_color(item.primary_color) for item in items) >= 2:
                score += 10.0
            if formality_consistency_score(items) >= 70:
                score += 8.0
        elif goal == "comfortable":
            if {"relaxed", "regular"} & fits:
                score += 16.0
            if "casual" in styles:
                score += 8.0
            if weather_score_value >= 70:
                score += 8.0
        goal_scores.append(clamp(score))

    return clamp(sum(goal_scores) / len(goal_scores))


def preference_score(
    items: tuple[ClothingItem, ClothingItem, ClothingItem],
    profile: UserProfile | None,
) -> float:
    score = 52.0
    styles = set().union(*(get_item_styles(item) for item in items))
    colors = {normalize_tag(item.primary_color or "") for item in items if item.primary_color}

    favorites = sum(item.is_favorite for item in items)
    score += favorites * 10.0

    if profile:
        preferred_styles = normalize_tags(profile.style_preferences)
        preferred_colors = normalize_tags(profile.color_preferences)
        avoid_tags = normalize_tags(profile.avoid_tags)

        if preferred_styles & styles:
            score += 14.0
        if preferred_colors & colors:
            score += 10.0
        if avoid_tags & styles:
            score -= 26.0

    return clamp(score)


def repetition_penalty(items: tuple[ClothingItem, ClothingItem, ClothingItem]) -> float:
    penalties: list[float] = []
    today = date.today()

    for item in items:
        if not item.last_worn_date:
            penalties.append(0.0)
            continue

        days_since = (today - item.last_worn_date).days
        if days_since <= 3:
            penalties.append(100.0)
        elif days_since <= 7:
            penalties.append(72.0)
        elif days_since <= 14:
            penalties.append(38.0)
        else:
            penalties.append(12.0)

    return clamp(sum(penalties) / len(penalties) if penalties else 0.0)


def is_valid_combination(
    top: ClothingItem,
    pants: ClothingItem,
    shoes: ClothingItem,
    request: RecommendationRequest,
) -> bool:
    items = (top, pants, shoes)
    if max(formality_value(item) for item in items) - min(formality_value(item) for item in items) > 1:
        style_sets = [get_item_styles(item) for item in items]
        pairwise_overlap = any(left & right for left, right in combinations(style_sets, 2))
        if not pairwise_overlap:
            return False

    target_seasons = WEATHER_TO_SEASONS.get(normalize_tag(request.weather), set())
    incompatible_items = 0
    for item in items:
        seasons = get_item_seasons(item)
        if seasons and target_seasons and not seasons & target_seasons:
            incompatible_items += 1

    return incompatible_items < 2


def calculate_outfit_score(
    top: ClothingItem,
    pants: ClothingItem,
    shoes: ClothingItem,
    profile: UserProfile | None,
    request: RecommendationRequest,
) -> ScoreResult:
    items = (top, pants, shoes)
    compatibility = compatibility_score(items, request.target_style)
    weather_score_value = weather_match_score(items, request.weather)
    user_fit = user_fit_score(items, profile, weather_score_value)
    style_match = style_match_score(items, request.target_style)
    scene_match = scene_match_score(items, request.target_scene)
    preference = preference_score(items, profile)
    repetition = repetition_penalty(items)

    total = (
        (0.30 * compatibility)
        + (0.20 * user_fit)
        + (0.20 * style_match)
        + (0.15 * scene_match)
        + (0.10 * weather_score_value)
        + (0.10 * preference)
        - (0.05 * repetition)
    )

    return ScoreResult(
        compatibility_score=round(clamp(compatibility), 2),
        user_fit_score=round(clamp(user_fit), 2),
        style_match_score=round(clamp(style_match), 2),
        scene_match_score=round(clamp(scene_match), 2),
        weather_match_score=round(clamp(weather_score_value), 2),
        preference_score=round(clamp(preference), 2),
        repetition_penalty=round(clamp(repetition), 2),
        total_score=round(clamp(total), 2),
    )


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))
