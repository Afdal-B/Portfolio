"""Project catalog combining the repository and online edits.

Two ways to change the catalog must both work: pushing a new
storage/projects.json, and editing online on a host whose filesystem is
read-only (Vercel). So Upstash doesn't hold a full copy of the catalog (a
push would then never show), only the online changes relative to the
repository, each remembering a fingerprint of the repository version it was
made on:

- a project edited online replaces the repository version, as long as that
  version is unchanged; once a push changes it, the repository wins again;
- a project deleted online stays hidden under the same condition;
- a project created online exists online only;
- a project added by a push appears, at the end of any order set online.
"""

import hashlib
import json
import uuid
from dataclasses import replace
from typing import Any, Optional, Sequence

from app.adapters.outbound.persistence.json_project_repository import (
    assign_ids,
    project_from_dict,
    project_to_dict,
)
from app.adapters.outbound.upstash import UpstashClient
from app.domain.models import Project
from app.domain.ports import ProjectRepository

KEY = "pf:projects:changes"
# Earlier format: the whole catalog. Converted to changes on first read.
LEGACY_KEY = "pf:projects"


def fingerprint(project: Project) -> str:
    payload = json.dumps(project_to_dict(project), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class UpstashProjectRepository:
    def __init__(self, client: UpstashClient, seed: ProjectRepository) -> None:
        self._client = client
        self._seed = seed  # the catalog shipped in the repository

    def list_all(self) -> list[Project]:
        shipped = self._seed.list_all()
        changes = self._changes(shipped)
        if changes is None:
            return shipped
        return _merge(shipped, changes)

    def replace_all(self, projects: Sequence[Project]) -> list[Project]:
        shipped = self._seed.list_all()
        stored = _assign_ids(projects, taken={p.id for p in shipped})
        self._client.set(KEY, json.dumps(_diff(shipped, stored), ensure_ascii=False))
        return stored

    def _changes(self, shipped: list[Project]) -> Optional[dict[str, Any]]:
        raw = self._client.get(KEY)
        if raw is not None:
            return json.loads(raw)
        legacy = self._client.get(LEGACY_KEY)
        if legacy is None:
            return None
        # The legacy key held the catalog as last saved online: whatever
        # differs from the repository becomes an online change.
        changes = _diff(shipped, [project_from_dict(item) for item in json.loads(legacy)])
        self._client.set(KEY, json.dumps(changes, ensure_ascii=False))
        return changes


def _diff(shipped: Sequence[Project], wanted: Sequence[Project]) -> dict[str, Any]:
    """What makes `wanted` out of the repository catalog `shipped`."""
    by_id = {p.id: p for p in shipped}
    wanted_ids = {p.id for p in wanted}
    edited = {}
    for project in wanted:
        base = by_id.get(project.id)
        if base is not None and project == base:
            continue  # same as the repository: nothing to remember
        edited[project.id] = {
            "project": project_to_dict(project),
            "base": fingerprint(base) if base is not None else None,
        }
    deleted = {p.id: fingerprint(p) for p in shipped if p.id not in wanted_ids}
    return {"edited": edited, "deleted": deleted, "order": [p.id for p in wanted]}


def _merge(shipped: Sequence[Project], changes: dict[str, Any]) -> list[Project]:
    by_id = {p.id: p for p in shipped}
    edited: dict[str, Any] = changes.get("edited", {})
    deleted: dict[str, str] = changes.get("deleted", {})

    def current(project_id: str) -> Optional[Project]:
        base = by_id.get(project_id)
        if project_id in deleted:
            # Hidden while the repository version is the one deleted.
            return base if base is not None and fingerprint(base) != deleted[project_id] else None
        if project_id in edited:
            change = edited[project_id]
            if base is None or fingerprint(base) == change["base"]:
                return project_from_dict(change["project"])
            return base  # changed in the repository since: the push wins
        return base

    order = list(changes.get("order", []))
    order += [p.id for p in shipped if p.id not in order]  # added by a push
    result = []
    for project_id in order:
        project = current(project_id)
        if project is not None:
            result.append(project)
    return result


def _assign_ids(projects: Sequence[Project], taken: set[str]) -> list[Project]:
    """Ids for projects created online, never reusing a repository project's
    id: an online project would otherwise shadow it."""
    in_list = {p.id for p in projects if p.id}
    stored = assign_ids(projects)
    result = []
    for before, after in zip(projects, stored):
        if not before.id and after.id in taken - in_list:
            after = replace(after, id=f"{after.id}-{uuid.uuid4().hex[:4]}")
        result.append(after)
    return result
