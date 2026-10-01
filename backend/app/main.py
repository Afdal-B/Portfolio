"""FastAPI entrypoint — an inbound adapter, nothing more: it wires HTTP
concerns (CORS, routers) onto the services built by the
composition root in app/container.py."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.inbound.http import routes_admin, routes_analytics, routes_chat, routes_content, routes_uploads
from app.container import container

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    retriever = container.retriever
    # On a long-running server, index now so the first question is fast. On
    # Vercel, every instance would pay for it, including those that only
    # serve page content: the chat service indexes on first use instead.
    if retriever is not None and not os.environ.get("VERCEL"):
        try:
            retriever.warm_up(("fr", "en"))
            container.chat_service
        except Exception:
            # The page content doesn't need the index: a failure here must
            # not take the whole API down. The chat falls back to scripted
            # answers until indexing succeeds.
            logger.exception("Warm-up of the retrieval index failed")
    yield


app = FastAPI(title="Afdal Bouraima Portfolio API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=container.settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_chat.router, prefix="/api")
app.include_router(routes_content.router, prefix="/api")
app.include_router(routes_admin.router, prefix="/api")
app.include_router(routes_analytics.router, prefix="/api")
app.include_router(routes_uploads.router, prefix="/api")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
