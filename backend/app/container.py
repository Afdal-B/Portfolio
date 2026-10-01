"""Composition root: the one place that knows both the ports and the
adapters, and wires them together.

Everything is built lazily and memoized, so importing this module costs
nothing: in particular, no API client is created and no Chroma client is
opened until something actually asks for the retriever."""

import os
from functools import cached_property
from pathlib import Path
from typing import Optional

from app.adapters.outbound.llm.gemini_answer_generator import GeminiAnswerGenerator
from app.adapters.outbound.llm.scripted_answer_generator import ScriptedAnswerGenerator
from app.adapters.outbound.persistence.filesystem_image_store import FilesystemImageStore
from app.adapters.outbound.persistence.json_project_repository import JsonProjectRepository
from app.adapters.outbound.persistence.static_content_repository import (
    StaticContactRepository,
    StaticCopyRepository,
    StaticExperienceRepository,
    StaticQARepository,
    StaticSkillRepository,
)
from app.adapters.outbound.rag.chroma_retriever import DEFAULT_CHROMA_PATH, ChromaRetriever
from app.adapters.outbound.rag.embedder import GeminiEmbedder
from app.adapters.outbound.rag.embedding_cache import CachedEmbedder
from app.adapters.outbound.rag.markdown_knowledge_repository import MarkdownKnowledgeRepository
from app.config import Settings, settings as default_settings
from app.domain.models import Chunk
from app.domain.project_chunking import LANGS, overview_chunk, project_chunk
from app.domain.ports import AnswerGenerator, Retriever
from app.domain.services.chat_service import ChatService
from app.domain.services.content_service import ContentService
from app.domain.services.project_service import ProjectService


class Container:
    def __init__(self, settings: Settings = default_settings) -> None:
        self.settings = settings

    # --- outbound adapters ---------------------------------------------

    @cached_property
    def project_repository(self) -> JsonProjectRepository:
        return JsonProjectRepository()

    @cached_property
    def image_store(self) -> FilesystemImageStore:
        return FilesystemImageStore()

    @cached_property
    def qa_repository(self) -> StaticQARepository:
        return StaticQARepository()

    @cached_property
    def copy_repository(self) -> StaticCopyRepository:
        return StaticCopyRepository()

    @cached_property
    def retriever(self) -> Optional[Retriever]:
        """Only built when an LLM is configured: without one the scripted
        generator answers, and nothing would ever query the vector store."""
        if not self.settings.gemini_api_key:
            return None
        return ChromaRetriever(
            knowledge=MarkdownKnowledgeRepository(),
            embedder=CachedEmbedder(
                GeminiEmbedder(
                    self.settings.gemini_api_key,
                    self.settings.embedding_model,
                    self.settings.embedding_dimensions,
                ),
                self.settings.embedding_model,
                self.settings.embedding_dimensions,
            ),
            chroma_path=self._chroma_path(),
        )

    def _chroma_path(self) -> Path:
        if self.settings.chroma_path:
            return Path(self.settings.chroma_path)
        # Vercel sets VERCEL=1 in its functions, where only /tmp is writable.
        if os.environ.get("VERCEL"):
            return Path("/tmp/chroma")
        return DEFAULT_CHROMA_PATH

    @cached_property
    def primary_generator(self) -> Optional[AnswerGenerator]:
        if not self.settings.gemini_api_key:
            return None
        return GeminiAnswerGenerator(self.settings.gemini_api_key, self.settings.gemini_model)

    @cached_property
    def scripted_generator(self) -> AnswerGenerator:
        return ScriptedAnswerGenerator(self.qa_repository, self.copy_repository)

    def indexed_chunks(self) -> list[Chunk]:
        """Every passage the vector store holds, in both languages: the
        knowledge documents and the project catalog. What the embedding
        cache must cover."""
        projects = self.project_repository.list_all()
        chunks: list[Chunk] = []
        for lang in LANGS:
            chunks.extend(MarkdownKnowledgeRepository().chunks(lang))
            chunks.extend(project_chunk(project, lang) for project in projects)
            if projects:
                chunks.append(overview_chunk(projects, lang))
        return chunks

    # --- domain services -------------------------------------------------

    @cached_property
    def chat_service(self) -> ChatService:
        # The vector store must know the projects before the first question.
        # Done here rather than only at startup: serverless hosts may start
        # an instance without running the app's startup hook.
        self.project_service.sync_index()
        return ChatService(
            fallback_generator=self.scripted_generator,
            copy=self.copy_repository,
            primary_generator=self.primary_generator,
            retriever=self.retriever,
            top_k=self.settings.rag_top_k,
            min_score=self.settings.rag_min_score,
        )

    @cached_property
    def content_service(self) -> ContentService:
        return ContentService(
            experiences=StaticExperienceRepository(),
            skills=StaticSkillRepository(),
            contacts=StaticContactRepository(),
            qa=self.qa_repository,
        )

    @cached_property
    def project_service(self) -> ProjectService:
        return ProjectService(
            repository=self.project_repository,
            image_store=self.image_store,
            retriever=self.retriever,
        )


container = Container()
