from fastapi import FastAPI

app = FastAPI(title="MusicSync API", version="0.1.0")


@app.get("/api/v1/health", tags=["health"])
def health() -> dict[str, str]:
    """Return a lightweight health check for local development and CI."""
    return {"status": "ok"}
