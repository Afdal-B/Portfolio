"""FastAPI entrypoint — an inbound adapter, nothing more: it wires HTTP
concerns (CORS, routers, static files) onto the services built by the
composition root in app/container.py."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.adapters.inbound.http import routes_admin, routes_chat, routes_content
from app.adapters.outbound.persistence.filesystem_image_store import DEFAULT_UPLOAD_DIR, URL_PREFIX
from app.container import container


@asynccontextmanager
async def lifespan(app: FastAPI):
    retriever = container.retriever
    if retriever is not None:
        # Indexes the documents and the project catalog now, so the first
        # visitor doesn't wait for it. Where the host skips this hook
        # (serverless), building the chat service does it on first use.
        retriever.warm_up(("fr", "en"))
        container.chat_service
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

# Images uploaded through the admin UI, served read-only. Created only when
# missing: on a read-only filesystem (serverless), it ships with the code.
if not DEFAULT_UPLOAD_DIR.exists():
    DEFAULT_UPLOAD_DIR.mkdir(parents=True)
app.mount(URL_PREFIX, StaticFiles(directory=DEFAULT_UPLOAD_DIR), name="uploads")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
