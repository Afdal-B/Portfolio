# Portfolio d'Afdal Bouraima

Portfolio de développeur IA : une page classique et lisible (projets,
expérience, compétences, contact), plus un **assistant RAG** qui répond aux
questions sur mon parcours à partir de mon CV. Bilingue FR/EN, thème clair et
sombre.

## Structure

- `frontend/` : React, TypeScript, Vite, Tailwind CSS v4
- `backend/` : FastAPI (Python 3.11, dépendances gérées avec Poetry), en
  **architecture hexagonale**

### Backend : ports et adaptateurs

```
backend/app/
├── domain/                 # cœur métier, sans aucune dépendance framework
│   ├── models.py           # dataclasses (Project, Answer, Chunk…)
│   ├── ports.py            # interfaces (Protocols) dont le domaine a besoin
│   ├── intent_router.py    # routage par mots-clés du mode scripté
│   ├── project_chunking.py # comment un projet est décrit au retrieval
│   └── services/           # cas d'usage : chat, contenu, projets
├── adapters/
│   ├── inbound/http/       # FastAPI : routes, DTO Pydantic, limite de requêtes
│   └── outbound/
│       ├── persistence/    # catalogue de projets (JSON), contenu statique, images
│       ├── rag/            # documents Markdown, embeddings, ChromaDB
│       └── llm/            # Gemini et répondeur scripté (même port)
├── config.py               # configuration (pydantic-settings)
├── container.py            # composition root
└── main.py                 # point d'entrée FastAPI
```

Les dépendances pointent uniquement vers l'intérieur : le domaine n'importe
ni FastAPI, ni Pydantic, ni ChromaDB, ni le SDK Gemini. La règle est vérifiée
par [`tests/test_architecture.py`](backend/tests/test_architecture.py).

## L'assistant RAG

Pipeline de bout en bout, sans framework d'orchestration :

1. **Documents** : un CV en prose, [`content/afdal.fr.md`](backend/content/afdal.fr.md)
   et [`afdal.en.md`](backend/content/afdal.en.md), plus le catalogue de
   projets, [`storage/projects.json`](backend/storage/projects.json).
2. **Découpage** : une section `##` par passage, catégorisée (profil,
   expérience, compétences…) ; un passage par projet, et un passage de vue
   d'ensemble qui les nomme tous.
3. **Embeddings** : API Gemini (`gemini-embedding-001`, 768 dimensions), avec
   des types de tâche distincts pour les passages et pour les questions.
   Les vecteurs des passages sont pré-calculés dans
   [`content/embeddings.json`](backend/content/embeddings.json) (`make embeddings`
   après chaque modification du contenu) : une instance qui démarre indexe le
   corpus sans appeler l'API, seule la question du visiteur est vectorisée.
4. **Index** : ChromaDB, une collection par langue, construit au démarrage
   (ou à la première question sur Vercel) et mis à jour quand le catalogue
   change.
5. **Génération** : Gemini (`gemini-3.5-flash-lite`) répond en Markdown à
   partir des seuls passages retrouvés, avec la date du jour pour situer les
   expériences dans le temps.

Les sources et la confiance affichées sont calculées à partir du score de
similarité, jamais déclarées par le modèle. Sans clé Gemini, ou si l'appel
échoue, un répondeur scripté par mots-clés prend le relais. Le chat est
limité à 20 questions par heure et par visiteur, pour protéger le quota
gratuit de Gemini.

## Mesure d'audience

Visites et questions posées à l'assistant sont comptées sans cookie et sans
conserver d'adresse IP : un visiteur est reconnu au sein d'une même journée
par une empreinte salée qui change chaque jour. Le pays et la ville viennent
des en-têtes de géolocalisation de Vercel. Les chiffres sont stockés dans
Upstash Redis (offre gratuite), dans des clés qui expirent seules : 400 jours
pour les compteurs, 90 jours pour le texte des questions.

## Développement

Prérequis : Node 20+, [Poetry](https://python-poetry.org) et Python 3.11+.

```bash
cp backend/.env.example backend/.env   # puis renseigner la clé Gemini
make install
make dev-backend     # terminal 1 : http://localhost:8000
make dev-frontend    # terminal 2 : http://localhost:5173 (proxy /api vers :8000)
```

Tests : `make test` (pytest côté backend, build côté frontend).

## Déploiement

Tout le site est déployé sur **Vercel**, dans un seul projet, grâce aux
[Services](https://vercel.com/docs/services) déclarés dans [`vercel.json`](vercel.json) :

- `frontend/` est construit avec Vite et servi pour toutes les adresses ;
- `backend/` tourne comme fonction Python (FastAPI) et reçoit `/api/*`.

Chaque push sur `main` redéploie les deux. Variables d'environnement du projet
Vercel : `PORTFOLIO_GEMINI_API_KEY`, et celles d'Upstash Redis, ajoutées par
son intégration Vercel.

Le disque des fonctions est en lecture seule, sauf `/tmp` où l'index ChromaDB
est reconstruit à chaque démarrage d'instance. L'état partagé vit donc dans
Upstash Redis :

- le catalogue de projets et ses images (`storage/projects.json` et
  `storage/uploads/` n'en sont que la version initiale) ;
- les vecteurs des passages calculés après le déploiement, pour qu'un passage
  ne soit vectorisé qu'une fois, toutes instances confondues ;
- les statistiques d'audience.

Avant chaque question, une instance vérifie que son index correspond au
catalogue actuel et le met à jour sinon. Après une modification des documents
`content/afdal.*.md`, on lance `make embeddings` avant de pousser ; un test
échoue si on l'oublie.

Pour un hébergement Docker classique, [`backend/Dockerfile`](backend/Dockerfile)
construit l'image du backend : un volume monté sur `/app/storage` y conserve
le catalogue et les images.
