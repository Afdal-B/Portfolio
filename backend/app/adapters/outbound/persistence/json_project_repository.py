"""Project catalog persisted as JSON on disk, so the admin API can update it
at runtime without a redeploy."""

import json
import re
import unicodedata
import uuid
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

from app.domain.models import Project

DEFAULT_STORAGE_PATH = Path(__file__).resolve().parents[4] / "storage" / "projects.json"


def _slugify(value: str) -> str:
    # Strip accents first so "Détoxification" becomes "detoxification" rather
    # than losing the accented letters to separators.
    decomposed = unicodedata.normalize("NFKD", value.lower())
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")
    return slug[:48]


class JsonProjectRepository:
    def __init__(self, storage_path: Path = DEFAULT_STORAGE_PATH) -> None:
        self._path = storage_path

    def list_all(self) -> list[Project]:
        if not self._path.exists():
            return []
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        return [self._to_domain(item) for item in raw]

    def replace_all(self, projects: Sequence[Project]) -> list[Project]:
        stored = self._ensure_ids(projects)
        payload = [self._to_storage(project) for project in stored]
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return stored

    def _ensure_ids(self, projects: Sequence[Project]) -> list[Project]:
        """Assigns a stable id to any project that doesn't have one yet (i.e.
        newly created through the admin UI), keeping existing ids untouched."""
        used = {project.id for project in projects if project.id}
        result: list[Project] = []
        for project in projects:
            if project.id:
                result.append(project)
                continue
            base = _slugify(project.title.get("fr") or project.title.get("en") or "") or uuid.uuid4().hex[:8]
            candidate = base
            while candidate in used:
                candidate = f"{base}-{uuid.uuid4().hex[:4]}"
            used.add(candidate)
            result.append(replace(project, id=candidate))
        return result

    def _to_domain(self, item: dict[str, Any]) -> Project:
        return Project(
            id=item.get("id", ""),
            meta=item["meta"],
            title=item["title"],
            result=item["result"],
            problem=item["problem"],
            method=item["method"],
            stack=item["stack"],
            metrics=item["metrics"],
            url=item.get("url", "#"),
            image_url=item.get("image_url", ""),
            screenshots=list(item.get("screenshots", [])),
            image_seed=item.get("image_seed", ""),
            summary=dict(item.get("summary", {})),
            code_url=item.get("code_url", ""),
        )

    def _to_storage(self, project: Project) -> dict[str, Any]:
        return {
            "id": project.id,
            "meta": project.meta,
            "title": project.title,
            "result": project.result,
            "problem": project.problem,
            "method": project.method,
            "stack": project.stack,
            "metrics": project.metrics,
            "url": project.url,
            "image_url": project.image_url,
            "screenshots": project.screenshots,
            "image_seed": project.image_seed,
            "summary": project.summary,
            "code_url": project.code_url,
        }
