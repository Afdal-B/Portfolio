"""Scripted Q&A content — real content about Afdal Bouraima (sourced from his
LinkedIn profile), structured after the `qa` array in the design prototype
(Portfolio Afdal Bouraima v2.dc.html, lines 341-362). Used directly by the
legacy keyword router, and indirectly by the RAG corpus (app/rag/corpus.py)."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QAEntry:
    id: str
    q: dict[str, str]
    a: dict[str, str]
    sources: Optional[dict[str, list[str]]] = None
    confidence: Optional[int] = None
    hidden: bool = False


QA: dict[str, QAEntry] = {
    "profile": QAEntry(
        id="profile",
        q={"fr": "Son profil en une phrase", "en": "His profile in one sentence"},
        a={
            "fr": (
                "Afdal est développeur IA, spécialisé en NLP et LLM. Pendant son alternance "
                "chez ContentSide (2025-2026, terminée), il a conçu et déployé des fonctionnalités IA pour "
                "une plateforme SaaS utilisée par des clients presse : classification hiérarchique de texte, "
                "évaluation de systèmes RAG, extraction d'information par vision-langage. "
                "Diplômé d'un Master en IA (MALIA, Université Lyon 2), il a aussi mené des "
                "recherches sur la détoxification de texte multilingue au Laboratoire ERIC."
            ),
            "en": (
                "Afdal is an AI developer specialized in NLP and LLMs. During his "
                "apprenticeship at ContentSide (2025-2026, now completed), he built and shipped AI "
                "features for a SaaS platform used by press clients: hierarchical text classification, RAG evaluation, "
                "vision-language information extraction. He holds a Master's in AI "
                "(MALIA, Université Lyon 2), and previously researched multilingual "
                "text detoxification at Laboratoire ERIC."
            ),
        },
        sources={
            "fr": ["CV : synthèse de profil", "Projets : fiches détaillées"],
            "en": ["CV: profile summary", "Projects: detailed records"],
        },
        confidence=94,
    ),
    "experience": QAEntry(
        id="experience",
        q={"fr": "Son expérience professionnelle", "en": "His professional experience"},
        a={
            "fr": (
                "Trois expériences :\n"
                "- **Développeur IA chez ContentSide** (Lyon, alternance, sept. 2025 à sept. 2026, terminée) : classification hiérarchique d'articles, évaluation RAG par LLM-as-a-judge et extraction de tags par VLM, pour des clients presse.\n"
                "- **R&D en NLP au Laboratoire ERIC** (Bron, stage, avril à août 2025) : détoxification de texte multilingue, challenge TextDetox sur 15 langues.\n"
                "- **Développeur web chez 57Informatique** (Sarrebourg, stage, avril à juin 2024) : annuaire professionnel full-stack avec paiement Stripe."
            ),
            "en": (
                "Three roles:\n"
                "- **AI developer at ContentSide** (Lyon, apprenticeship, Sept. 2025 to Sept. 2026, completed): hierarchical article classification, RAG evaluation with LLM-as-a-judge and VLM-based tag extraction, for press clients.\n"
                "- **NLP R&D at Laboratoire ERIC** (Bron, internship, April to August 2025): multilingual text detoxification, TextDetox challenge across 15 languages.\n"
                "- **Web developer at 57Informatique** (Sarrebourg, internship, April to June 2024): full-stack business directory with Stripe payments."
            ),
        },
        sources={
            "fr": ["CV : expériences professionnelles"],
            "en": ["CV: professional experience"],
        },
        confidence=96,
    ),
    "avail": QAEntry(
        id="avail",
        q={"fr": "Disponibilité & CDI", "en": "Availability & permanent role"},
        a={
            "fr": (
                "Afdal a terminé son alternance chez ContentSide en septembre 2026 et "
                "est disponible immédiatement. Il recherche un CDI d'ingénieur IA, NLP ou "
                "MLOps, ou de data scientist. Il est mobile dans toute la France et ouvert "
                "au sur site, à l'hybride comme au télétravail complet."
            ),
            "en": (
                "Afdal completed his apprenticeship at ContentSide in September 2026 "
                "and is available immediately. He is looking for a permanent role as an "
                "AI, NLP or MLOps engineer, or as a data scientist. He is open to "
                "relocating anywhere in France, on-site, hybrid or fully remote."
            ),
        },
        sources={
            "fr": ["Recherche : statut déclaré", "Préférences de poste"],
            "en": ["Search: declared status", "Role preferences"],
        },
        confidence=99,
    ),
    "projects": QAEntry(
        id="projects",
        q={"fr": "Voir les projets", "en": "See the projects"},
        a={
            # No count here: the catalog is edited through the admin, so a
            # hardcoded number would silently go stale.
            "fr": (
                "Ses projets sont présentés dans la section Projets de cette page, chacun avec une démo "
                "en ligne et ses résultats chiffrés. Demandez-moi le détail de l'un d'eux : la méthode, "
                "la stack ou les métriques."
            ),
            "en": (
                "His projects are shown in the Projects section of this page, each with a live demo and "
                "measured results. Ask me about any of them: the method, the stack or the metrics."
            ),
        },
        sources={
            "fr": ["Projets : fiches détaillées", "Résultats et métriques"],
            "en": ["Projects: detailed records", "Results and metrics"],
        },
        confidence=92,
    ),
    "skills": QAEntry(
        id="skills",
        q={"fr": "Compétences", "en": "Skills"},
        a={
            "fr": (
                "- **NLP et LLM** : Transformers (Hugging Face), LangChain, LangGraph, RAG, fine-tuning LoRA et PEFT, NER, classification.\n"
                "- **Machine learning** : PyTorch, TensorFlow, Scikit-learn, XGBoost, NumPy, Pandas, Matplotlib.\n"
                "- **Séries temporelles et vision** : ARIMA, SARIMA, LSTM, YOLO.\n"
                "- **MLOps et cloud** : MLflow, Docker, Git, Azure, GCP, Scaleway.\n"
                "- **Langages et web** : Python, SQL, R, Java, JavaScript, FastAPI, React."
            ),
            "en": (
                "- **NLP and LLMs**: Transformers (Hugging Face), LangChain, LangGraph, RAG, LoRA and PEFT fine-tuning, NER, classification.\n"
                "- **Machine learning**: PyTorch, TensorFlow, Scikit-learn, XGBoost, NumPy, Pandas, Matplotlib.\n"
                "- **Time series and vision**: ARIMA, SARIMA, LSTM, YOLO.\n"
                "- **MLOps and cloud**: MLflow, Docker, Git, Azure, GCP, Scaleway.\n"
                "- **Languages and web**: Python, SQL, R, Java, JavaScript, FastAPI, React."
            ),
        },
        sources={
            "fr": ["Compétences : auto-évaluation", "Projets : usages réels"],
            "en": ["Skills: self-assessment", "Projects: real usage"],
        },
        confidence=85,
    ),
    "nocv": QAEntry(
        id="nocv",
        hidden=True,
        q={
            "fr": "Le CV est-il téléchargeable ?",
            "en": "Is the CV downloadable?",
        },
        a={
            "fr": (
                "Le CV n'est pas proposé en téléchargement sur ce site. Posez-moi "
                "vos questions sur le parcours, les projets, les compétences ou la "
                "disponibilité, ou écrivez directement à Afdal à "
                "afdalbouraima2@gmail.com pour en discuter."
            ),
            "en": (
                "The CV is not available for download on this site. Ask me about "
                "the background, projects, skills or availability, or email Afdal "
                "directly at afdalbouraima2@gmail.com to talk it through."
            ),
        },
    ),
    "contact": QAEntry(
        id="contact",
        q={"fr": "Me contacter", "en": "Get in touch"},
        a={
            "fr": (
                "Le plus simple est d'écrire à afdalbouraima2@gmail.com, ou de passer par LinkedIn. "
                "Réponse sous 24 heures, du lundi au vendredi. Tous les liens sont en bas de la page."
            ),
            "en": (
                "The easiest way is to email afdalbouraima2@gmail.com, or to reach out on LinkedIn. "
                "Reply within 24 hours, Monday to Friday. All the links are at the bottom of the page."
            ),
        },
    ),
    "team": QAEntry(
        id="team",
        q={
            "fr": "Travaille-t-il avec des non-techniciens ?",
            "en": "Does he work with non-technical people?",
        },
        a={
            "fr": (
                "Oui. Chez ContentSide, il a travaillé avec des clients presse "
                "non-techniques : chaque solution IA était conçue pour répondre à un "
                "besoin métier concret, puis livrée et validée directement par le "
                "client avant sa mise en production."
            ),
            "en": (
                "Yes. At ContentSide, he worked with non-technical press clients: "
                "every AI solution was designed to answer a concrete business need, "
                "then delivered and validated directly by the client before going "
                "into production."
            ),
        },
        sources={
            "fr": ["Projets : phase de cadrage", "Retours d'équipe"],
            "en": ["Projects: framing phase", "Team feedback"],
        },
        confidence=82,
    ),
}

# Order matches the `qa` array in the prototype — drives suggestion chip order.
QA_ORDER: list[str] = ["profile", "experience", "avail", "projects", "skills", "nocv", "contact", "team"]

# Retry chips for the fallback response (prototype line 681: ["projects", "skills", "avail"]).
RETRY_IDS: list[str] = ["projects", "skills", "avail"]
