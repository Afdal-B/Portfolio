# Afdal Bouraima

## Profil
Afdal est développeur IA, spécialisé en NLP et LLM. Il a effectué son alternance chez ContentSide de septembre 2025 à septembre 2026. Cette alternance est terminée : il ne travaille plus chez ContentSide et il est disponible immédiatement pour un nouveau poste. Pendant cette alternance, il a conçu et déployé des fonctionnalités IA pour une plateforme SaaS utilisée par des clients presse : classification hiérarchique de texte, évaluation de systèmes RAG, extraction d'information par vision-langage. Il a aussi mené des recherches sur la détoxification de texte multilingue au Laboratoire ERIC. Au-delà du NLP, il a pratiqué la prévision de séries temporelles et la détection d'objets en vision par ordinateur. Il est basé à Lyon, en Auvergne-Rhône-Alpes. Il parle français (langue maternelle) et anglais (niveau professionnel).

## Formation
Afdal est diplômé du Master MALIA (Machine Learning pour l'Intelligence Artificielle) de l'Université Lumière Lyon 2, suivi de 2024 à 2026, en alternance chez ContentSide pendant la deuxième année. Auparavant, il a obtenu une Licence à l'Université de Lorraine, de 2021 à 2024, où il a construit ses bases en statistiques, algorithmes et NLP. Il a effectué le cinquième semestre de cette Licence en Erasmus à l'University of Eastern Finland, à l'automne 2023. Il n'a pas de publication scientifique ni de certification à mentionner.

## Disponibilité
Afdal a terminé son alternance chez ContentSide en septembre 2026 et est disponible immédiatement. Il recherche un CDI en France, sur des postes d'ingénieur IA ou Machine Learning, d'ingénieur NLP ou LLM, de data scientist ou d'ingénieur MLOps. Il est mobile dans toute la France et ouvert à toutes les organisations du travail : sur site, hybride ou télétravail complet. Ses prétentions salariales se discutent directement avec lui, selon le poste.

## Collaboration non-technique
Chez ContentSide, Afdal a travaillé avec des clients presse non-techniques : chaque solution IA était conçue pour répondre à un besoin métier concret, puis livrée et validée directement par le client avant sa mise en production.

## Expérience : ContentSide
Afdal a été développeur IA en alternance chez ContentSide, à Lyon (sur site), de septembre 2025 à septembre 2026 (1 an). Ce poste est terminé. Il y a construit et déployé des fonctionnalités IA pour la Semantic Platform, un produit SaaS utilisé par de grands clients presse. Il a recherché et implémenté des solutions IA adaptées aux besoins clients, du prototype à la mise en production. Il a benchmarké des modèles de reconnaissance d'entités (NER) pour améliorer le service existant de la plateforme. Il a construit un pipeline complet de classification hiérarchique d'articles : préparation des données, entraînement du modèle, suivi des expériences avec MLflow, analyse des performances et déploiement en production. Il a conçu et implémenté un pipeline d'évaluation RAG utilisant l'approche LLM-as-a-judge, permettant à l'équipe de mesurer la qualité des réponses et de cibler les axes d'amélioration. Il a aussi mené une revue de l'état de l'art et développé une solution d'extraction de tags sur des caricatures de presse, combinant des modèles vision-langage (VLM) et un dictionnaire de tags pour identifier personnalités publiques et thèmes. Solution livrée et validée par le client. Stack technique chez ContentSide : Python, PyTorch, LangChain, vLLM, Ollama, MLflow, FastAPI, Java, Kotlin, Quarkus, PostgreSQL, Milvus, Elasticsearch, GCP et Scaleway.

## Expérience : Laboratoire ERIC
Stage de recherche et développement en NLP au Laboratoire ERIC, à Bron (sur site), d'avril à août 2025 (5 mois). Afdal a participé au challenge international TextDetox sur la détoxification de texte multilingue, couvrant 15 langues, à l'aide de grands modèles de langage. Il a mené des recherches et effectué du fine-tuning de modèles pour la réécriture de texte toxique. Stack technique au Laboratoire ERIC : Python, Transformers (Hugging Face), LLM, fine-tuning LoRA et QLoRA.

## Expérience : 57Informatique
Stage de développeur web chez 57Informatique, à Sarrebourg (sur site), d'avril à juin 2024 (3 mois). Afdal a développé un site vitrine d'annuaire professionnel full-stack, avec un système de gestion des annonces et un paiement sécurisé intégré via Stripe. Stack technique chez 57Informatique : PHP, JavaScript, React, HTML et CSS.

## Projet académique : prévision de consommation électrique (séries temporelles)
Projet du cours Temporal Data Analysis du Master MALIA, réalisé en binôme en 2025-2026, en R. Objectif : prévoir la consommation électrique d'un bâtiment, mesurée toutes les 15 minutes, pour une journée complète (96 valeurs), avec la température extérieure comme variable explicative possible. L'exploration a mis en évidence une double saisonnalité, journalière et hebdomadaire, traitée par différenciation. Afdal et son binôme ont comparé de nombreuses approches : lissage exponentiel (Holt-Winters), régression linéaire (tslm), SARIMA automatique et manuel (identifié à partir des ACF/PACF), ARIMAX avec la température, réseaux de neurones auto-régressifs (NNAR), réseaux récurrents LSTM en prévision récursive et directe, puis SVR, Random Forest et XGBoost sur des fenêtres de 96 retards, après tuning des hyperparamètres. Le meilleur modèle est le SVR, avec un RMSE de 14,15 et un MAPE de 4 % en utilisant la température, devant le SARIMA manuel (RMSE 14,58) et XGBoost (14,69). Ce modèle a été réentraîné sur toutes les données pour produire la prévision finale.

## Projet personnel : détection d'objets avec YOLO (vision par ordinateur)
Projet personnel de vision par ordinateur. Afdal a constitué son propre jeu de données en scrapant des photos de setups (postes de travail), a annoté les objets présents selon plusieurs classes avec Roboflow, puis a entraîné un modèle YOLO à détecter et classer ces objets.

## Compétences
Langages : Python, SQL, R, Java, Kotlin, JavaScript, C, C++, C#, Node.js, PHP, HTML et CSS.
Machine Learning et Deep Learning : PyTorch, TensorFlow, Scikit-learn, XGBoost, NumPy, Pandas, Matplotlib, réseaux récurrents (LSTM).
NLP et LLM : reconnaissance d'entités nommées (NER), classification de texte, Transformers (Hugging Face), LangChain, LangGraph, fine-tuning (LoRA, QLoRA, PEFT), RAG, évaluation de LLM (LLM-as-a-judge), service de modèles avec vLLM et Ollama.
Séries temporelles : lissage exponentiel, ARIMA, SARIMA et ARIMAX, NNAR, LSTM, approches machine learning sur retards (SVR, Random Forest, XGBoost).
Vision par ordinateur : détection d'objets avec YOLO, annotation avec Roboflow, modèles vision-langage (VLM).
Data et bases de données : PySpark, Power BI, PostgreSQL, MySQL, MongoDB, Elasticsearch, bases vectorielles (Milvus, Zilliz).
Cloud et MLOps : Azure, GCP, Scaleway, Docker, MLflow, Git, CI/CD.
Web : FastAPI, React, Spring Boot, Quarkus.

## Ce site
Ce portfolio est lui-même un projet d'Afdal. L'assistant qui répond aux questions est un système RAG de bout en bout : un CV rédigé en prose est découpé en passages, chaque passage est transformé en embedding avec l'API Gemini (modèle gemini-embedding-001), puis stocké dans un index vectoriel ChromaDB. À chaque question, les passages les plus proches sont retrouvés et Gemini rédige la réponse à partir de ces seuls passages. Si le modèle est indisponible, un répondeur scripté prend le relais. Le backend est écrit en FastAPI selon une architecture hexagonale, le frontend en React avec TypeScript, et l'ensemble est déployé sur Vercel.

## Contact
Pour contacter Afdal : par email à afdalbouraima2@gmail.com, ou sur LinkedIn (linkedin.com/in/afdal-bouraima-276183253). Son code est sur GitHub (github.com/Afdal-B) et ses modèles sur Hugging Face (huggingface.co/Dalfaxy). Réponse sous 24 heures, du lundi au vendredi. Le CV n'est pas proposé en téléchargement direct sur ce site : il est préférable de le contacter directement pour en discuter.
