"""Repositories over the static content modules in ./static_data.

The literal content keeps its own storage-shaped dataclasses; this adapter
maps them into domain models, so the domain never sees the storage format
(e.g. the QA module's terse `q`/`a` fields, or skill glyphs stored as keys
into a lookup table)."""

import re
from dataclasses import replace
from typing import Optional

from app.adapters.outbound.persistence.static_data.contacts import CONTACTS
from app.adapters.outbound.persistence.static_data.copy import COPY
from app.adapters.outbound.persistence.static_data.experience import EXPERIENCES
from app.adapters.outbound.persistence.static_data.qa import QA, QA_ORDER
from app.adapters.outbound.persistence.static_data.skills import GLYPHS, GROUP_ORDER, GROUPS, TECH
from app.domain.models import Contact, Experience, Lang, QAEntry, Skill, SkillGroup


def _skill(name: str) -> Skill:
    entry = TECH[name]
    # Glyphs are stored as a key; the domain wants the paths.
    return Skill(name=entry.name, icon=entry.icon, glyph=GLYPHS[entry.glyph] if entry.glyph else None)


class StaticExperienceRepository:
    def list_all(self) -> list[Experience]:
        return [
            Experience(
                company=entry.company,
                role=entry.role,
                contract_type=entry.contract_type,
                period=entry.period,
                location=entry.location,
                context=entry.context,
                bullets=entry.bullets,
                stack=[_skill(name) for name in entry.stack],
            )
            for entry in EXPERIENCES
        ]


# Case-insensitive index, so "Pytorch" in an admin-typed stack still matches.
_TECH_BY_LOWER = {name.lower(): name for name in TECH}


class StaticSkillRepository:
    def resolve(self, name: str) -> Skill:
        # Ignore a trailing precision: "PySpark (ALS)" is PySpark, "Azure
        # (Container Apps, ...)" is Azure. The displayed name stays as written.
        key = re.sub(r"\s*\(.*\)\s*$", "", name).strip().lower()
        known = _TECH_BY_LOWER.get(key)
        if known is None:
            return Skill(name=name)
        return replace(_skill(known), name=name)

    def list_all(self) -> list[SkillGroup]:
        groups: list[SkillGroup] = []
        for group_id in GROUP_ORDER:
            group = GROUPS[group_id]
            groups.append(
                SkillGroup(
                    id=group_id,
                    title=group.title,
                    skills=[_skill(name) for name in group.skills],
                )
            )
        return groups


class StaticContactRepository:
    def list_all(self) -> list[Contact]:
        return [Contact(key=entry.key, value=entry.value, href=entry.href) for entry in CONTACTS]


class StaticQARepository:
    def list_all(self) -> list[QAEntry]:
        return [self._to_domain(qa_id) for qa_id in QA_ORDER]

    def get(self, entry_id: str) -> Optional[QAEntry]:
        if entry_id not in QA:
            return None
        return self._to_domain(entry_id)

    def _to_domain(self, entry_id: str) -> QAEntry:
        entry = QA[entry_id]
        return QAEntry(
            id=entry.id,
            question=entry.q,
            answer=entry.a,
            sources=entry.sources,
            confidence=entry.confidence,
            hidden=entry.hidden,
        )


class StaticCopyRepository:
    def fallback_text(self, lang: Lang) -> str:
        return COPY[lang]["fallback"]
