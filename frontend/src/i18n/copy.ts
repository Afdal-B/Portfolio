import type { Lang } from "../types/chat"

export const copy = {
  fr: {
    // Header
    navProjects: "Projets",
    navExperience: "Expérience",
    navSkills: "Compétences",
    navAssistant: "Assistant",
    contactBtn: "Me contacter",
    themeLabel: "Thème clair / sombre",
    langLabel: "Langue",

    // Hero
    available: "Disponible immédiatement · CDI en France",
    location: "Lyon · mobile",
    pitch: "Je transforme des modèles en systèmes fiables.",
    intro:
      "Développeur IA spécialisé en NLP, RAG et LLM. Je conçois des fonctionnalités IA et je les mène jusqu'à la production, dernièrement chez ContentSide pour des clients presse.",
    seeProjects: "Voir les projets",
    askAssistant: "Poser une question à mon assistant",
    atAGlance: "En bref",
    lastRoleLabel: "Dernier poste",
    lastRole: "Développeur IA chez ContentSide",
    lastRoleDetail: "Alternance, de septembre 2025 à septembre 2026",
    educationLabel: "Formation",
    education: "Master MALIA, Université Lyon 2",
    educationDetail: "Machine Learning pour l'Intelligence Artificielle",
    specialtiesLabel: "Spécialités",
    specialties: [
      "NLP",
      "LLM",
      "RAG",
      "Deep Learning",
      "Computer Vision",
      "Séries temporelles",
      "Évaluation de LLM",
      "MLOps",
    ],

    // Projects
    projectsLead: "Des projets en ligne, testables tout de suite.",
    demo: "Voir la démo",
    code: "Code",
    model: "Modèle",
    details: "Détails",
    imageAlt: (title: string) => `Capture de ${title}`,

    // Experience
    stack: "Stack",
    stackLabel: "Stack technique",
    loading: "Chargement…",
    loadError: "Ce contenu est momentanément indisponible. Rechargez la page dans un instant.",
    showDetails: "Voir le détail",
    hideDetails: "Masquer le détail",

    // Assistant
    assistantKicker: "Assistant RAG",
    assistantTitle: "Une question précise ? Demandez à mon assistant.",
    buildTitle: "Comment ce site est construit",
    buildLead: "L'assistant est lui-même un projet : un RAG de bout en bout.",
    buildSteps: [
      "Un CV en prose, découpé en passages",
      "Embeddings calculés avec l'API Gemini",
      "Index vectoriel ChromaDB",
      "Réponse de Gemini, à partir des seuls passages retrouvés",
      "Repli scripté si le modèle est indisponible",
    ],

    // Contact
    contactTitle: "Travaillons ensemble",
    contactLead: "Réponse sous 24 heures, du lundi au vendredi.",
    privacy: "Mesure d'audience anonyme : ni cookie, ni adresse IP conservée.",
    chatPrivacy: "Les questions posées sont conservées 90 jours, sans donnée d'identification, pour améliorer l'assistant.",

    // Chat
    shots: "Aperçus",
    visit: "Voir la démo",
    inputPlaceholder: "Posez votre question…",
    traceSources: "Sources utilisées",
    traceConfidence: "Confiance",
    traceLabel: "voir comment cette réponse a été construite",
    traceHide: "masquer le détail",
    close: "Fermer",
    you: "vous",
    bot: "assistant",
    greeting:
      "Bonjour, je suis l'assistant d'Afdal. Je réponds à partir de son parcours, de ses projets et de ses compétences. Que voulez-vous savoir ?",
    fallback:
      "Je réponds à partir du dossier d'Afdal : parcours, projets, compétences, disponibilité et contact. Reformulez votre question, ou choisissez l'une des suggestions sous la conversation.",
    problem: "Problème",
    method: "Méthode",
    metrics: "Métriques",
    engineScripted: "réponse scriptée",
    engineRag: "généré par l'IA",
    requestFailed: "Je n'arrive pas à joindre le serveur pour le moment. Réessayez dans un instant.",
    rateLimited:
      "Vous avez posé beaucoup de questions en peu de temps : réessayez dans une heure, ou écrivez directement à Afdal à afdalbouraima2@gmail.com.",
    send: "Envoyer",
  },
  en: {
    navProjects: "Projects",
    navExperience: "Experience",
    navSkills: "Skills",
    navAssistant: "Assistant",
    contactBtn: "Get in touch",
    themeLabel: "Light / dark theme",
    langLabel: "Language",

    available: "Available now · Permanent role in France",
    location: "Lyon · open to relocation",
    pitch: "I turn models into reliable systems.",
    intro:
      "AI developer specialised in NLP, RAG and LLMs. I design AI features and take them all the way to production, most recently at ContentSide for press clients.",
    seeProjects: "See the projects",
    askAssistant: "Ask my assistant a question",
    atAGlance: "At a glance",
    lastRoleLabel: "Latest role",
    lastRole: "AI Developer at ContentSide",
    lastRoleDetail: "Apprenticeship, September 2025 to September 2026",
    educationLabel: "Education",
    education: "MALIA Master's, Université Lyon 2",
    educationDetail: "Machine Learning for Artificial Intelligence",
    specialtiesLabel: "Specialties",
    specialties: [
      "NLP",
      "LLMs",
      "RAG",
      "Deep learning",
      "Computer vision",
      "Time series",
      "LLM evaluation",
      "MLOps",
    ],

    projectsLead: "Live projects you can try right away.",
    demo: "Try the demo",
    code: "Code",
    model: "Model",
    details: "Details",
    imageAlt: (title: string) => `Screenshot of ${title}`,

    stack: "Stack",
    stackLabel: "Tech stack",
    loading: "Loading…",
    loadError: "This content is temporarily unavailable. Reload the page in a moment.",
    showDetails: "Show details",
    hideDetails: "Hide details",

    assistantKicker: "RAG assistant",
    assistantTitle: "A specific question? Ask my assistant.",
    buildTitle: "How this site is built",
    buildLead: "The assistant is a project in itself: an end-to-end RAG.",
    buildSteps: [
      "A prose CV, split into passages",
      "Embeddings computed with the Gemini API",
      "ChromaDB vector index",
      "Gemini answers from the retrieved passages only",
      "Scripted fallback when the model is unavailable",
    ],

    contactTitle: "Let's work together",
    contactLead: "Reply within 24 hours, Monday to Friday.",
    privacy: "Anonymous audience measurement: no cookies, no IP address stored.",
    chatPrivacy: "Questions are kept for 90 days, with no identifying data, to improve the assistant.",

    shots: "Screenshots",
    visit: "Try the demo",
    inputPlaceholder: "Ask your question…",
    traceSources: "Sources used",
    traceConfidence: "Confidence",
    traceLabel: "see how this answer was built",
    traceHide: "hide the details",
    close: "Close",
    you: "you",
    bot: "assistant",
    greeting:
      "Hello, I'm Afdal's assistant. I answer from his background, projects and skills. What would you like to know?",
    fallback:
      "I answer from Afdal's file: background, projects, skills, availability and contact. Try rephrasing, or pick one of the suggestions below the conversation.",
    problem: "Problem",
    method: "Method",
    metrics: "Metrics",
    engineScripted: "scripted answer",
    engineRag: "AI-generated",
    requestFailed: "I can't reach the server right now. Try again in a moment.",
    rateLimited:
      "You've asked a lot of questions in a short time: try again in an hour, or email Afdal directly at afdalbouraima2@gmail.com.",
    send: "Send",
  },
} as const

export function t(lang: Lang) {
  return copy[lang]
}
