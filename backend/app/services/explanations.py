from __future__ import annotations

from app.models.clothing import ClothingItem
from app.models.profile import UserProfile
from app.models.recommendation import RecommendationRequest
from app.services.scoring import ScoreResult, is_neutral_color


def _color_sentence(top: ClothingItem, pants: ClothingItem, shoes: ClothingItem) -> str:
    top_color = (top.primary_color or "").lower()
    pants_color = (pants.primary_color or "").lower()
    shoes_color = (shoes.primary_color or "").lower()
    neutral_count = sum(is_neutral_color(color) for color in [top_color, pants_color, shoes_color])

    if neutral_count >= 2:
        return "The mostly neutral palette keeps the outfit looking clean and easy to style."

    if top_color and pants_color and top_color != pants_color:
        return "The lighter-to-darker contrast between the top and pants gives the outfit balanced structure."

    return "The colors stay coordinated without making the outfit feel too flat."


def _goal_sentence(profile: UserProfile | None, score: ScoreResult) -> str:
    if not profile or not profile.body_goals:
        return "It also stays close to the comfort and polish balance that works well for daily wear."

    primary_goal = profile.body_goals[0].replace("-", " ")
    if score.user_fit_score >= 75:
        return f"It leans into your goal to {primary_goal} with a more intentional silhouette."
    return f"It still nods to your goal to {primary_goal} while keeping the outfit practical."


def _scene_sentence(request: RecommendationRequest, top: ClothingItem, shoes: ClothingItem) -> str:
    shoes_formality = (shoes.formality or "casual").lower()
    if request.target_scene == "work":
        return "The shoe choice keeps the outfit polished enough for work without feeling stiff."
    if request.target_scene == "date":
        return "The overall mix feels put-together but not overdressed for a date setting."
    if request.target_scene == "school":
        return "The outfit stays relaxed enough for school while still feeling intentional."
    if shoes_formality == "casual":
        return "The shoes keep the outfit relaxed instead of pushing it too formal."
    return "The outfit stays adaptable for an easy outing."


def generate_explanation(
    top: ClothingItem,
    pants: ClothingItem,
    shoes: ClothingItem,
    profile: UserProfile | None,
    request: RecommendationRequest,
    score: ScoreResult,
) -> str:
    style_descriptor = request.target_style.strip() or "preferred"
    intro = f"This outfit matches your {style_descriptor} direction for {request.target_scene}."
    middle = _color_sentence(top, pants, shoes)

    if score.weather_match_score >= 70:
        ending = f"It should also feel right for {request.weather} weather."
    elif score.scene_match_score >= 70:
        ending = _scene_sentence(request, top, shoes)
    else:
        ending = _goal_sentence(profile, score)

    return " ".join([intro, middle, ending])
