from fastapi import FastAPI

from opspilot.api.incidents import router as incidents_router


app = FastAPI(
    title="OpsPilot API",
    version="0.1.0",
    )

app.include_router(incidents_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}