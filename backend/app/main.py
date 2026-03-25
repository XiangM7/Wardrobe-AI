from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import UPLOAD_DIR
from app.database import create_db_and_tables
from app.routers import clothing, demo, feedback, profiles, recommendations, try_on, users


app = FastAPI(
    title="Wardrobe AI API",
    description="Rule-based wardrobe recommendation API for the Wardrobe AI MVP.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "Wardrobe AI API"}


app.include_router(users.router)
app.include_router(demo.router)
app.include_router(profiles.router)
app.include_router(clothing.router)
app.include_router(recommendations.router)
app.include_router(feedback.router)
app.include_router(try_on.router)
