"""Project catalog kept in Upstash Redis, so it can be edited online on a
host whose filesystem is read-only (Vercel). Until the first save, the
catalog shipped with the code (storage/projects.json) is served."""

import json
from typing import Sequence

from app.adapters.outbound.persistence.json_project_repository import (
    assign_ids,
    project_from_dict,
    project_to_dict,
)
from app.adapters.outbound.upstash import UpstashClient
from app.domain.models import Project
from app.domain.ports import ProjectRepository

KEY = "pf:projects"


class UpstashProjectRepository:
    def __init__(self, client: UpstashClient, seed: ProjectRepository) -> None:
        self._client = client
        self._seed = seed

    def list_all(self) -> list[Project]:
        raw = self._client.get(KEY)
        if raw is None:
            return self._seed.list_all()
        return [project_from_dict(item) for item in json.loads(raw)]

    def replace_all(self, projects: Sequence[Project]) -> list[Project]:
        stored = assign_ids(projects)
        self._client.set(KEY, json.dumps([project_to_dict(p) for p in stored], ensure_ascii=False))
        return stored
