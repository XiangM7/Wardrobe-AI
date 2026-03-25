import unittest

from app.models.clothing import ClothingItem
from app.models.profile import UserProfile
from app.models.recommendation import RecommendationRequest
from app.services.scoring import calculate_outfit_score


def build_item(
    *,
    category: str,
    primary_color: str,
    style_tags: list[str],
    season_tags: list[str],
    formality: str,
    fit: str,
) -> ClothingItem:
    return ClothingItem(
        user_id=1,
        image_path=f"uploads/clothing_items/{category}.png",
        category=category,
        primary_color=primary_color,
        secondary_color=None,
        style_tags=style_tags,
        season_tags=season_tags,
        formality=formality,
        fit=fit,
        brand=f"{category}-brand",
        is_favorite=False,
    )


class ScoringTests(unittest.TestCase):
    def test_goal_aligned_clean_outfit_scores_higher(self) -> None:
        profile = UserProfile(
            user_id=1,
            full_body_image_path=None,
            style_preferences=["clean", "minimal"],
            body_goals=["look taller", "look cleaner"],
            color_preferences=["white", "navy"],
            avoid_tags=["loud"],
            notes=None,
        )
        request = RecommendationRequest(
            user_id=1,
            target_style="clean",
            target_scene="school",
            weather="mild",
            extra_note=None,
        )

        high_score = calculate_outfit_score(
            build_item(
                category="tops",
                primary_color="white",
                style_tags=["clean", "minimal"],
                season_tags=["spring", "summer"],
                formality="casual",
                fit="regular",
            ),
            build_item(
                category="pants",
                primary_color="navy",
                style_tags=["clean", "minimal"],
                season_tags=["spring", "autumn"],
                formality="casual",
                fit="slim",
            ),
            build_item(
                category="shoes",
                primary_color="navy",
                style_tags=["clean", "casual"],
                season_tags=["spring", "autumn"],
                formality="casual",
                fit="regular",
            ),
            profile,
            request,
        )

        low_score = calculate_outfit_score(
            build_item(
                category="tops",
                primary_color="red",
                style_tags=["street"],
                season_tags=["winter"],
                formality="casual",
                fit="oversized",
            ),
            build_item(
                category="pants",
                primary_color="green",
                style_tags=["street"],
                season_tags=["winter"],
                formality="casual",
                fit="relaxed",
            ),
            build_item(
                category="shoes",
                primary_color="orange",
                style_tags=["street"],
                season_tags=["winter"],
                formality="formal",
                fit="regular",
            ),
            profile,
            request,
        )

        self.assertGreater(high_score.total_score, low_score.total_score)
        self.assertGreater(high_score.style_match_score, low_score.style_match_score)
        self.assertGreater(high_score.user_fit_score, low_score.user_fit_score)


if __name__ == "__main__":
    unittest.main()
