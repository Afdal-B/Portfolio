# Afdal Bouraima

## Profile
Afdal is an AI developer specialized in NLP and LLMs. He did his apprenticeship at ContentSide from September 2025 to September 2026. That apprenticeship has ended: he no longer works at ContentSide and is available immediately for a new role. During it, he built and shipped AI features for a SaaS platform used by press clients: hierarchical text classification, RAG evaluation, vision-language information extraction. He also researched multilingual text detoxification at Laboratoire ERIC. Beyond NLP, he has worked on time series forecasting and on object detection in computer vision. He is based in Lyon, France. He speaks French (native) and English (professional level).

## Education
Afdal holds the MALIA Master's degree (Machine Learning for Artificial Intelligence) from Université Lumière Lyon 2, completed between 2024 and 2026, with the second year done as an apprenticeship at ContentSide. Before that, he earned a Bachelor's degree at Université de Lorraine, from 2021 to 2024, where he built his foundation in statistics, algorithms and NLP. He spent the fifth semester of that Bachelor's on an Erasmus exchange at the University of Eastern Finland, in autumn 2023. He has no scientific publications or certifications to report.

## Availability
Afdal completed his apprenticeship at ContentSide in September 2026 and is available immediately. He is looking for a permanent role in France, as an AI or machine learning engineer, NLP or LLM engineer, data scientist or MLOps engineer. He is open to relocating anywhere in France and to any working arrangement: on-site, hybrid or fully remote. Salary expectations are discussed directly with him, depending on the role.

## Non-technical collaboration
At ContentSide, Afdal worked with non-technical press clients: every AI solution was designed to answer a concrete business need, then delivered and validated directly by the client before going into production.

## Experience: ContentSide
Afdal was an AI developer apprentice at ContentSide, in Lyon (on-site), from September 2025 to September 2026 (1 year). This role has ended. He built and shipped AI features for the Semantic Platform, a SaaS product used by major press clients. He researched and implemented AI solutions tailored to client needs, from proof of concept to production deployment. He benchmarked named-entity recognition (NER) models to improve the platform's existing entity recognition service. He built an end-to-end pipeline for hierarchical article classification: data preparation, model training, experiment tracking with MLflow, performance analysis and production deployment. He designed and implemented a RAG evaluation pipeline using the LLM-as-a-judge approach, letting the team measure answer quality and pinpoint areas for improvement. He also conducted a state-of-the-art review and developed a tag extraction solution for press caricatures, combining vision-language models (VLMs) with a tag dictionary to identify public figures and themes. The solution was delivered and validated by the client. Tech stack at ContentSide: Python, PyTorch, LangChain, vLLM, Ollama, MLflow, FastAPI, Java, Kotlin, Quarkus, PostgreSQL, Milvus, Elasticsearch, GCP and Scaleway.

## Experience: Laboratoire ERIC
NLP research and development internship at Laboratoire ERIC, in Bron (on-site), from April to August 2025 (5 months). Afdal competed in the international TextDetox challenge on multilingual text detoxification, covering 15 languages, using large language models. He conducted research and fine-tuned models for toxic text rewriting. Tech stack at Laboratoire ERIC: Python, Transformers (Hugging Face), LLMs, LoRA and QLoRA fine-tuning.

## Experience: 57Informatique
Web developer internship at 57Informatique, in Sarrebourg (on-site), from April to June 2024 (3 months). Afdal developed a full-stack business directory website, with an ad management system and secure payment integration via Stripe. Tech stack at 57Informatique: PHP, JavaScript, React, HTML and CSS.

## Academic project: electricity consumption forecasting (time series)
Project for the Temporal Data Analysis course of the MALIA Master's, done in a pair in 2025-2026, in R. Goal: forecast a building's electricity consumption, measured every 15 minutes, for a full day ahead (96 values), with the outdoor temperature available as an explanatory variable. Exploration revealed a double seasonality, daily and weekly, handled by differencing. Afdal and his teammate compared many approaches: exponential smoothing (Holt-Winters), linear regression (tslm), automatic and manual SARIMA (identified from ACF/PACF plots), ARIMAX with temperature, neural network autoregression (NNAR), LSTM recurrent networks with recursive and direct forecasting, then SVR, Random Forest and XGBoost on 96-lag windows, after hyperparameter tuning. The best model was SVR, with an RMSE of 14.15 and a MAPE of 4% using temperature, ahead of manual SARIMA (RMSE 14.58) and XGBoost (14.69). That model was retrained on all the data to produce the final forecast.

## Personal project: object detection with YOLO (computer vision)
Personal computer vision project. Afdal built his own dataset by scraping photos of desk setups, annotated the objects in them by class with Roboflow, then trained a YOLO model to detect and classify those objects.

## Skills
Languages: Python, SQL, R, Java, Kotlin, JavaScript, C, C++, C#, Node.js, PHP, HTML and CSS.
Machine Learning and Deep Learning: PyTorch, TensorFlow, Scikit-learn, XGBoost, NumPy, Pandas, Matplotlib, recurrent networks (LSTM).
NLP and LLMs: named-entity recognition (NER), text classification, Transformers (Hugging Face), LangChain, LangGraph, fine-tuning (LoRA, QLoRA, PEFT), RAG, LLM evaluation (LLM-as-a-judge), model serving with vLLM and Ollama.
Time series: exponential smoothing, ARIMA, SARIMA and ARIMAX, NNAR, LSTM, machine learning on lagged features (SVR, Random Forest, XGBoost).
Computer vision: object detection with YOLO, annotation with Roboflow, vision-language models (VLMs).
Data and databases: PySpark, Power BI, PostgreSQL, MySQL, MongoDB, Elasticsearch, vector databases (Milvus, Zilliz).
Cloud and MLOps: Azure, GCP, Scaleway, Docker, MLflow, Git, CI/CD.
Web: FastAPI, React, Spring Boot, Quarkus.

## This site
This portfolio is itself one of Afdal's projects. The assistant answering questions is an end-to-end RAG system: a prose CV is split into passages, each passage is embedded with the Gemini API (gemini-embedding-001 model) and stored in a ChromaDB vector index. For each question, the closest passages are retrieved and Gemini writes the answer from those passages only. If the model is unavailable, a scripted responder takes over. The backend is written in FastAPI with a hexagonal architecture, the frontend in React with TypeScript, and the whole site is deployed on Vercel.

## Contact
To reach Afdal: by email at afdalbouraima2@gmail.com, or on LinkedIn (linkedin.com/in/afdal-bouraima-276183253). His code is on GitHub (github.com/Afdal-B) and his models on Hugging Face (huggingface.co/Dalfaxy). Reply within 24 hours, Monday to Friday. The CV is not available for direct download on this site: it's best to reach out directly to discuss it.
