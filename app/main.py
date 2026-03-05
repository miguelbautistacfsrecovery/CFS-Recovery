from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="Thriver AI", version="1.0.0")

# Import routers after app creation to avoid circular imports
from app.auth import router as auth_router
from app.billing import router as billing_router
from app.rag import router as rag_router

app.include_router(auth_router, prefix="/api/auth")
app.include_router(billing_router, prefix="/api/billing")
app.include_router(rag_router, prefix="/api")

# Serve static files
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def serve_index():
    return FileResponse(str(static_dir / "index.html"))
