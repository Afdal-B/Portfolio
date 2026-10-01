"""Keyword-routing rules, ported verbatim from `onSubmit` in the design
prototype (Portfolio Afdal Bouraima v2.dc.html, lines 730-739).

NB: this order does NOT match the design README's prose description of intent
priority — the prototype's own README states the source script is the source
of truth for exact keywords/order, so this list mirrors the code, not the
prose. Pure function, no I/O: this is domain logic."""

ROUTING_RULES: list[tuple[str, list[str]]] = [
    ("projects", ["projet", "project", "réalis", "livré", "delivered", "portfolio", "résultat", "result"]),
    ("skills", ["compét", "skill", "stack", "techno", "tool", "outil", "niveau", "level"]),
    (
        "experience",
        ["expérience", "poste occupé", "entreprise", "employeur", "alternance", "stage", "career", "experience", "employer", "company", "internship"],
    ),
    ("nocv", ["cv", "resume", "télécharg", "download", "pdf"]),
    ("contact", ["contact", "mail", "email", "joindre", "linkedin", "github", "reach"]),
    ("avail", ["cdi", "disponib", "available", "permanent", "france", "salaire", "mobilit"]),
    ("team", ["non-tech", "métier", "équipe", "team", "business", "communi", "vulgaris"]),
    ("profile", ["profil", "profile", "qui", "who", "parcours", "background", "présent"]),
]


def route(text: str) -> str:
    low = text.lower()
    for intent, keywords in ROUTING_RULES:
        if any(word in low for word in keywords):
            return intent
    return "fallback"
