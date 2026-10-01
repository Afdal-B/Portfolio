"""How a project is described to the retrieval system.

This is domain policy — the wording that ends up in the vector store — so it
lives in the core rather than in the Chroma adapter. The hand-written
knowledge document deliberately contains no project sections; these chunks
are the single retrieval source for projects."""

from typing import Sequence

from app.domain.models import Chunk, Lang, Project

PROJECT_SOURCE = "admin_project"

LANGS: tuple[Lang, ...] = ("fr", "en")

_LABELS: dict[str, dict[str, str]] = {
    "fr": {
        "problem": "Problème",
        "method": "Méthode",
        "stack": "Stack",
        "result": "Résultat",
        "metrics": "Métriques",
        "demo": "Démo en ligne",
        "code": "Code ou modèle",
    },
    "en": {
        "problem": "Problem",
        "method": "Method",
        "stack": "Stack",
        "result": "Result",
        "metrics": "Metrics",
        "demo": "Live demo",
        "code": "Code or model",
    },
}


def chunk_id(project_id: str, lang: Lang) -> str:
    return f"{lang}-admin-project-{project_id}"


def project_chunk(project: Project, lang: Lang) -> Chunk:
    label = _LABELS[lang]
    text = (
        f"{project.title.get(lang, '')} ({project.meta.get(lang, '')}). "
        f"{label['problem']} : {project.problem.get(lang, '')} "
        f"{label['method']} : {project.method.get(lang, '')} "
        f"{label['stack']} : {project.stack}. "
        f"{label['result']} : {project.result.get(lang, '')}"
    )
    metrics = project.metrics.get(lang, "").strip()
    if metrics:
        text += f" {label['metrics']} : {metrics}"
    if project.url and project.url != "#":
        text += f" {label['demo']} : {project.url}"
    if project.code_url:
        text += f" {label['code']} : {project.code_url}"
    return Chunk(
        id=chunk_id(project.id, lang),
        lang=lang,
        category="projects",
        text=text,
        source_label=project.title.get(lang, project.id),
    )


_OVERVIEW: dict[str, dict[str, str]] = {
    "fr": {
        "label": "Projets : vue d'ensemble",
        "intro": "Vue d'ensemble des projets d'Afdal présentés dans la section Projets de ce site, chacun avec une démo en ligne :",
        "outro": "D'autres projets, académiques ou personnels, sans démo sur le site, sont décrits à part.",
    },
    "en": {
        "label": "Projects: overview",
        "intro": "Overview of Afdal's projects shown in the Projects section of this site, each with a live demo:",
        "outro": "Other academic or personal projects, without a demo on the site, are described separately.",
    },
}


def overview_chunk_id(lang: Lang) -> str:
    return f"{lang}-admin-projects-overview"


def overview_chunk(projects: Sequence[Project], lang: Lang) -> Chunk:
    """One chunk naming every catalog project. A broad question ("what are
    his projects?") retrieves only a few chunks; without this one, whichever
    single projects happen to score highest would hide the others."""
    words = _OVERVIEW[lang]
    lines = [
        f"- {p.title.get(lang, p.id)} ({p.meta.get(lang, '')}) : {p.summary.get(lang) or p.result.get(lang, '')}"
        for p in projects
    ]
    return Chunk(
        id=overview_chunk_id(lang),
        lang=lang,
        category="projects",
        text="\n".join([words["intro"], *lines, words["outro"]]),
        source_label=words["label"],
    )
