# Wardrobe AI

Wardrobe AI is a full-stack MVP web app for personalized outfit recommendations using a user's own closet. The app supports local profile creation, a full-body onboarding image, manual clothing metadata editing, and rule-based daily outfit recommendations with clear explanation text.

## MVP Features

- Create a simple local user profile
- Upload one full-body image during onboarding
- Save style preferences, body goals, color preferences, avoid tags, and notes
- Upload closet items for `tops`, `pants`, and `shoes`
- Edit clothing metadata after upload
- Generate top 3 outfit combinations from the user's own closet
- Show score breakdowns and short explanation text for every recommendation
- Save recommendation requests and view recommendation history
- Submit simple feedback on generated outfits

## Tech Stack

### Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS

### Backend

- FastAPI
- SQLAlchemy
- Pydantic

### Data and Storage

- SQLite
- Local file storage for uploads

## Project Structure

```text
Wardrobe AI/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── uploads/
│   │   ├── clothing_items/
│   │   └── profile_images/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── closet/
│   │   ├── history/
│   │   ├── onboarding/
│   │   ├── recommend/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   ├── lib/
│   ├── .env.example
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── .gitignore
└── README.md
```

## Backend Architecture

### Models

- `users`
- `user_profiles`
- `clothing_items`
- `recommendation_requests`
- `outfit_recommendations`
- `user_feedback`

### Schemas

- request and response models for users, profiles, clothing items, recommendations, and feedback

### Routers

- `POST /users`
- `GET /users/{user_id}`
- `POST /profiles/{user_id}`
- `GET /profiles/{user_id}`
- `POST /clothing/{user_id}`
- `GET /clothing/{user_id}`
- `PUT /clothing/item/{item_id}`
- `DELETE /clothing/item/{item_id}`
- `POST /recommend/{user_id}`
- `GET /recommend/history/{user_id}`
- `POST /feedback/{user_id}`

### Services

- `storage.py`
  - handles upload saving and cleanup
- `scoring.py`
  - deterministic rule-based outfit scoring
- `explanations.py`
  - template-based explanation text generation
- `recommendation_engine.py`
  - candidate generation, filtering, ranking, and persistence

## Recommendation Logic

The MVP recommendation engine is intentionally explicit and rule-based.

### Candidate generation

- Build every valid combination of:
  - 1 top
  - 1 pair of pants
  - 1 pair of shoes
- Filter out combinations with obvious formality or seasonal conflicts

### Score formula

```text
Total Score =
0.30 * compatibility_score
+ 0.20 * user_fit_score
+ 0.20 * style_match_score
+ 0.15 * scene_match_score
+ 0.10 * weather_match_score
+ 0.10 * preference_score
- 0.05 * repetition_penalty
```

### Rule-based factors

- `compatibility_score`
  - color coordination
  - style consistency
  - formality consistency
- `user_fit_score`
  - goals like looking taller, slimmer, cleaner, or more comfortable
- `style_match_score`
  - overlap between outfit style tags and target style
- `scene_match_score`
  - fit for contexts like school, work, date, or outing
- `weather_match_score`
  - season tag alignment with cold, mild, or hot weather
- `preference_score`
  - favorite items, preferred tags, and preferred colors
- `repetition_penalty`
  - recent wear history via `last_worn_date`

## Frontend Pages

- `/`
  - landing page with overview and call to action
- `/onboarding`
  - create local profile, upload full-body image, save preferences and goals
- `/closet`
  - upload clothing items and edit metadata
- `/recommend`
  - generate today's outfit recommendations and submit feedback
- `/history`
  - browse previous recommendation bundles

## Local Setup

### 1. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.

Uploaded images are stored under:

- `backend/uploads/profile_images/`
- `backend/uploads/clothing_items/`

The SQLite database is created automatically at:

- `backend/wardrobe_ai.db`

### 2. Start the frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

## API Notes

### Creating a user

`POST /users`

```json
{
  "name": "Alex Kim",
  "email": "alex@example.com"
}
```

### Creating or updating a profile

`POST /profiles/{user_id}`

Use `multipart/form-data` with:

- `full_body_image`
- `style_preferences`
- `body_goals`
- `color_preferences`
- `avoid_tags`
- `notes`

Comma-separated text fields are converted to string arrays on the backend.

### Uploading clothing

`POST /clothing/{user_id}`

Use `multipart/form-data` with:

- `image`
- `category`
- `primary_color`
- `secondary_color`
- `style_tags`
- `season_tags`
- `formality`
- `fit`
- `brand`
- `is_favorite`
- `last_worn_date`

### Requesting recommendations

`POST /recommend/{user_id}`

```json
{
  "target_style": "clean",
  "target_scene": "school",
  "weather": "mild",
  "extra_note": "Need to walk a lot today"
}
```

## Verification Notes

- Backend Python source was syntax-checked with:

```bash
python3 -m compileall backend/app
```

- Frontend dependency installation and full Next.js build were not run in this environment because project packages were not installed yet.

## Future Improvements

- Add authentication instead of local profile selection
- Add automatic metadata extraction from item images
- Add wardrobe calendar and wear rotation insights
- Add richer scene and event contexts
- Add user profile editing for name and email
- Add tests for scoring and API routes
- Add cloud object storage and production database support
