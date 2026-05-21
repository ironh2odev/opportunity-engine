from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.opportunities import router as opportunities_router
from app.routers.tailoring import router as tailoring_router

app = FastAPI(
    title="Opportunity Engine API",
    version="0.1.0",
    description="Mock-first API for opportunity operations and tailoring workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/policy/human-review")
def human_review_policy() -> dict[str, str]:
    return {
        "policy": "Applications and outreach remain draft-only until explicit human approval.",
    }


app.include_router(opportunities_router)
app.include_router(tailoring_router)
