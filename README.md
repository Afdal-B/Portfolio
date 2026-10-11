# Portfolio d'Afdal Bouraima

Mon portfolio de développeur IA, avec un assistant RAG qui répond aux
questions sur mon parcours : [www.afdal-bouraima.fr](https://www.afdal-bouraima.fr/)

## Stack

- **Frontend** : React, TypeScript, Vite, Tailwind CSS
- **Backend** : FastAPI en architecture hexagonale, Python 3.11, Poetry
- **RAG** : embeddings et génération avec l'API Gemini, index vectoriel en mémoire
- **Hébergement** : Vercel, avec Upstash Redis pour les données partagées

## Lancer en local

Prérequis : Node 20+, Python 3.11+ et [Poetry](https://python-poetry.org).

```bash
cp backend/.env.example backend/.env   # puis renseigner la clé Gemini
make install
make dev-backend     # terminal 1 : http://localhost:8000
make dev-frontend    # terminal 2 : http://localhost:5173
```

Tests : `make test`. Après une modification de `backend/content/afdal.*.md`,
lancer `make embeddings` avant de pousser.
