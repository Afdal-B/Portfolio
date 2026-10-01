"""Real professional experience for Afdal Bouraima, sourced from his LinkedIn
profile. Ordered most recent first."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperienceEntry:
    company: str
    role: dict[str, str]
    contract_type: dict[str, str]
    period: dict[str, str]
    location: dict[str, str]
    context: dict[str, str]
    bullets: dict[str, list[str]]
    stack: list[str]  # keys into skills.TECH


EXPERIENCES: list[ExperienceEntry] = [
    ExperienceEntry(
        company="ContentSide",
        role={"fr": "Développeur IA", "en": "AI Developer"},
        contract_type={"fr": "Alternance", "en": "Apprenticeship"},
        period={"fr": "Sept. 2025 à sept. 2026 · 1 an", "en": "Sept. 2025 to Sept. 2026 · 1 year"},
        location={"fr": "Lyon, sur site", "en": "Lyon, on-site"},
        context={
            "fr": (
                "Conception et déploiement de fonctionnalités IA pour la Semantic Platform, "
                "un produit SaaS utilisé par de grands clients presse. Chaque solution répondait "
                "à un besoin métier concret et était validée par le client avant sa mise en production."
            ),
            "en": (
                "Designed and shipped AI features for the Semantic Platform, a SaaS product used "
                "by major press clients. Each solution answered a concrete business need and was "
                "validated by the client before going into production."
            ),
        },
        bullets={
            "fr": [
                "Recherche et implémentation de solutions IA adaptées aux besoins clients, du POC à la mise en production.",
                "Benchmark de modèles de reconnaissance d'entités (NER) pour améliorer le service existant de la plateforme.",
                "Pipeline complet de classification hiérarchique d'articles : préparation des données, entraînement, suivi des expériences avec MLflow, analyse des performances et déploiement en production.",
                "Pipeline d'évaluation RAG par LLM-as-a-judge, qui permet à l'équipe de mesurer la qualité des réponses et de cibler les axes d'amélioration.",
                "Extraction de tags sur des caricatures de presse, combinant modèles vision-langage (VLM) et dictionnaire de tags pour identifier personnalités et thèmes. Solution livrée et validée par le client.",
            ],
            "en": [
                "Researched and implemented AI solutions tailored to client needs, from proof of concept to production.",
                "Benchmarked named-entity recognition (NER) models to improve the platform's existing service.",
                "End-to-end hierarchical article classification pipeline: data preparation, training, experiment tracking with MLflow, performance analysis and production deployment.",
                "RAG evaluation pipeline using LLM-as-a-judge, letting the team measure answer quality and target improvements.",
                "Tag extraction on press caricatures, combining vision-language models (VLMs) with a tag dictionary to identify public figures and themes. Delivered and validated by the client.",
            ],
        },
        stack=[
            "Python",
            "PyTorch",
            "LangChain",
            "vLLM",
            "Ollama",
            "MLflow",
            "FastAPI",
            "Java",
            "Kotlin",
            "Quarkus",
            "PostgreSQL",
            "Milvus",
            "Elasticsearch",
            "GCP",
            "Scaleway",
        ],
    ),
    ExperienceEntry(
        company="Laboratoire ERIC",
        role={"fr": "R&D en NLP", "en": "NLP research & development"},
        contract_type={"fr": "Stage", "en": "Internship"},
        period={"fr": "Avril à août 2025 · 5 mois", "en": "April to August 2025 · 5 months"},
        location={"fr": "Bron, sur site", "en": "Bron, on-site"},
        context={
            "fr": (
                "Stage de recherche sur la détoxification de texte multilingue : réécrire un message "
                "toxique en une version neutre qui conserve son sens, à l'aide de grands modèles de langage."
            ),
            "en": (
                "Research internship on multilingual text detoxification: rewriting a toxic message "
                "into a neutral version that keeps its meaning, using large language models."
            ),
        },
        bullets={
            "fr": [
                "Participation au challenge international TextDetox, couvrant 15 langues.",
                "Recherche et fine-tuning de LLM pour la réécriture de texte toxique, avec des méthodes d'adaptation efficaces (LoRA, QLoRA).",
            ],
            "en": [
                "Competed in the international TextDetox challenge, covering 15 languages.",
                "Researched and fine-tuned LLMs for toxic text rewriting, using parameter-efficient methods (LoRA, QLoRA).",
            ],
        },
        stack=["Python", "Transformers", "LLM", "LoRA", "QLoRA"],
    ),
    ExperienceEntry(
        company="57Informatique",
        role={"fr": "Développeur web", "en": "Web developer"},
        contract_type={"fr": "Stage", "en": "Internship"},
        period={"fr": "Avril à juin 2024 · 3 mois", "en": "April to June 2024 · 3 months"},
        location={"fr": "Sarrebourg, sur site", "en": "Sarrebourg, on-site"},
        context={
            "fr": "Développement full-stack d'un site vitrine d'annuaire professionnel, du code serveur à l'interface.",
            "en": "Full-stack development of a business directory website, from server code to interface.",
        },
        bullets={
            "fr": [
                "Système de gestion des annonces pour les professionnels référencés.",
                "Intégration d'un paiement sécurisé via Stripe.",
            ],
            "en": [
                "Ad management system for the listed businesses.",
                "Secure payment integration via Stripe.",
            ],
        },
        stack=["PHP", "JavaScript", "React", "HTML", "CSS"],
    ),
]
