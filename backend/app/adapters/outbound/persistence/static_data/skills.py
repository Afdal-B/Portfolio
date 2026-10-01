"""Technology catalog, skill families and glyph paths.

`TECH` is the single list of technologies the site can display, shared by
the skills section and the per-experience stacks so a technology always has
the same name and icon wherever it appears."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SkillEntry:
    name: str
    # Key into the frontend's bundled logo set (frontend/src/lib/techIcons.ts).
    icon: Optional[str] = None
    glyph: Optional[str] = None  # key into GLYPHS, for skills without a logo


@dataclass(frozen=True)
class SkillGroup:
    id: str
    title: dict[str, str]
    skills: list[str]  # keys into TECH


GLYPHS: dict[str, list[str]] = {
    "db": [
        "M3 5c0-1.66 4-3 9-3s9 1.34 9 3v14c0 1.66-4 3-9 3s-9-1.34-9-3z",
        "M3 12c0 1.66 4 3 9 3s9-1.34 9-3",
    ],
    "tag": [
        "M7 7h.01",
        "M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0l-7.2-7.2A2 2 0 0 1 3 12V5a2 2 0 0 1 2-2h7a2 2 0 0 1 1.4.6l7.2 7.2a2 2 0 0 1 0 2.6z",
    ],
    "layers": ["M4 7h7v5H4z", "M13 12h7v5h-7z", "M4 16h7v4H4z"],
    "search": ["M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z", "M21 21l-4.3-4.3"],
    "chart": ["M3 3v18h18", "M7 15v-4", "M12 17V8", "M17 17v-6"],
    "model": [
        "M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"
    ],
    "flow": ["M4 4h6v6H4z", "M14 14h6v6h-6z", "M10 7h4v10"],
}


def _tech(*entries: SkillEntry) -> dict[str, SkillEntry]:
    return {entry.name: entry for entry in entries}


TECH: dict[str, SkillEntry] = _tech(
    # Languages
    SkillEntry("Python", icon="python"),
    SkillEntry("SQL", glyph="db"),
    SkillEntry("R", icon="r"),
    SkillEntry("Java", icon="java"),
    SkillEntry("Kotlin", icon="kotlin"),
    SkillEntry("JavaScript", icon="javascript"),
    SkillEntry("C", icon="c"),
    SkillEntry("C++", icon="cplusplus"),
    SkillEntry("C#", icon="csharp"),
    SkillEntry("Node.js", icon="nodedotjs"),
    SkillEntry("PHP", icon="php"),
    SkillEntry("HTML", icon="html5"),
    SkillEntry("CSS", icon="css"),
    # Machine learning
    SkillEntry("PyTorch", icon="pytorch"),
    SkillEntry("TensorFlow", icon="tensorflow"),
    SkillEntry("Scikit-learn", icon="scikitlearn"),
    SkillEntry("NumPy", icon="numpy"),
    SkillEntry("Pandas", icon="pandas"),
    SkillEntry("Matplotlib", icon="matplotlib"),
    # NLP and LLMs
    SkillEntry("Transformers (Hugging Face)", icon="huggingface"),
    SkillEntry("Transformers", icon="huggingface"),
    SkillEntry("LangChain", icon="langchain"),
    SkillEntry("LangGraph", icon="langgraph"),
    SkillEntry("RAG", glyph="search"),
    SkillEntry("Fine-tuning (LoRA / PEFT)", glyph="model"),
    SkillEntry("LoRA", glyph="layers"),
    SkillEntry("QLoRA", glyph="layers"),
    SkillEntry("LLM", glyph="model"),
    SkillEntry("NER", glyph="tag"),
    SkillEntry("Classification", glyph="layers"),
    SkillEntry("vLLM", icon="vllm"),
    SkillEntry("Ollama", icon="ollama"),
    SkillEntry("Hugging Face", icon="huggingface"),
    SkillEntry("Sentence Transformers", icon="huggingface"),
    SkillEntry("BERTopic", glyph="layers"),
    SkillEntry("spaCy", icon="spacy"),
    SkillEntry("gensim", glyph="tag"),
    SkillEntry("PEFT", glyph="model"),
    SkillEntry("mT0-XL", glyph="model"),
    # Data
    SkillEntry("PySpark", icon="apachespark"),
    SkillEntry("PostgreSQL", icon="postgresql"),
    SkillEntry("MySQL", icon="mysql"),
    SkillEntry("MongoDB", icon="mongodb"),
    SkillEntry("Bases vectorielles (Milvus / Zilliz)", glyph="db"),
    SkillEntry("Milvus", icon="milvus"),
    SkillEntry("Elasticsearch", icon="elasticsearch"),
    SkillEntry("Power BI", glyph="chart"),
    # Cloud and MLOps
    SkillEntry("Azure", icon="azure"),
    SkillEntry("GCP", icon="googlecloud"),
    SkillEntry("Scaleway", icon="scaleway"),
    SkillEntry("Docker", icon="docker"),
    SkillEntry("MLflow", icon="mlflow"),
    SkillEntry("Git", icon="git"),
    SkillEntry("CI/CD", glyph="flow"),
    # Web
    SkillEntry("FastAPI", icon="fastapi"),
    SkillEntry("React", icon="react"),
    SkillEntry("Spring Boot", icon="springboot"),
    SkillEntry("Quarkus", icon="quarkus"),
    SkillEntry("Streamlit", icon="streamlit"),
    SkillEntry("Gradio", icon="gradio"),
)

GROUP_ORDER: list[str] = ["nlp", "ml", "cloud", "data", "lang"]

GROUPS: dict[str, SkillGroup] = {
    "nlp": SkillGroup(
        id="nlp",
        title={"fr": "NLP et LLM", "en": "NLP & LLMs"},
        skills=[
            "Transformers (Hugging Face)",
            "LangChain",
            "LangGraph",
            "RAG",
            "Fine-tuning (LoRA / PEFT)",
            "NER",
            "Classification",
        ],
    ),
    "ml": SkillGroup(
        id="ml",
        title={"fr": "Machine Learning", "en": "Machine learning"},
        skills=["PyTorch", "TensorFlow", "Scikit-learn", "NumPy", "Pandas", "Matplotlib"],
    ),
    "cloud": SkillGroup(
        id="cloud",
        title={"fr": "Cloud et MLOps", "en": "Cloud & MLOps"},
        skills=["Azure", "GCP", "Scaleway", "Docker", "MLflow", "Git", "CI/CD"],
    ),
    "data": SkillGroup(
        id="data",
        title={"fr": "Data", "en": "Data"},
        skills=["PySpark", "PostgreSQL", "MySQL", "MongoDB", "Bases vectorielles (Milvus / Zilliz)", "Power BI"],
    ),
    "lang": SkillGroup(
        id="lang",
        title={"fr": "Langages et web", "en": "Languages & web"},
        skills=[
            "Python",
            "SQL",
            "R",
            "Java",
            "JavaScript",
            "C",
            "C++",
            "C#",
            "Node.js",
            "FastAPI",
            "React",
            "Spring Boot",
            "Quarkus",
        ],
    ),
}
