<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/pr1tzy/pr1tzy/main/assets/header-light.svg" />
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/pr1tzy/pr1tzy/main/assets/header-dark.svg" />
  <img alt="Prithvi Singh — ML infrastructure and backend. Speed trace from a real Monza lap, 1:28.197 against a 1:25.750 ghost." src="https://raw.githubusercontent.com/pr1tzy/pr1tzy/main/assets/header-dark.svg" width="100%" />
</picture>

<sub>The trace above is a real lap: Monza, Lotus Exos 125 S1, recorded by
<a href="https://github.com/pr1tzy/ghostline">Ghostline</a>. Violet is my lap, cyan is the ghost.</sub>

I work on the systems side of machine learning. Distributed training, retrieval,
and the infrastructure that keeps models serving after the notebook is closed.

```
training     multi-node GPU pretraining of dense embedding models
retrieval    RAG over Qdrant and Neo4j, masking strategy ablations
backend      FastAPI, PostgreSQL, Alembic, REST
infra        AWS (ECS, S3, SQS, Cognito), Terraform, Docker, Slurm
shipped      ghostline.prithvisingh.fyi
```

---

## Selected work

| Project | What it does | Stack |
|---|---|---|
| **[Ghostline](https://github.com/pr1tzy/ghostline)** · [live](https://ghostline.prithvisingh.fyi) | Records Assetto Corsa laps at 60 Hz, logs the fastest drivers on the server as ghosts, and tells you corner by corner where the time went. Live dash for a second monitor. | Python, SQLite, Lua, vanilla JS |
| **[Self-healing LLM QA](https://github.com/pr1tzy/mlopsproject)** | QA service that evaluates every candidate model against a benchmark and live traffic, then rolls itself back when a deploy regresses. | DVC, MLflow, Jenkins, Transformers |
| **[ParkiSense](https://github.com/pr1tzy/ParkiSense)** | Early Parkinson's screening from keystroke dynamics and drawing tremor. Wavelet and time-frequency features into SVM and Random Forest. | scikit-learn, SciPy, Gradio |

---

## Currently

Backend engineer at AceLink Software Solutions, working on Python services and
AWS infrastructure.

Before that, eight months as a technical intern at **BharatGen (IIT Bombay)**,
working on distributed pretraining of dense embedding models on a multi-node GPU
cluster: masking strategy ablations through pretraining and SFT, Slurm cluster
tooling, and large-scale data migration to S3.

Reading about inference optimisation and distributed training internals.

---

## Stack

```
languages    Python, SQL, TypeScript, Lua
ml           PyTorch, Transformers, scikit-learn, XGBoost
training     Multi-node GPU, Slurm, Fabric, distributed data pipelines
retrieval    Qdrant, Neo4j, embeddings, RAG
mlops        DVC, MLflow, Jenkins, GitHub Actions
backend      FastAPI, SQLAlchemy, PostgreSQL, Alembic
infra        AWS, Terraform, Docker, Cloudflare
```

---

## Research

**Do UN Discussions Reduce Terrorism? An Empirical Study on Political Stability
and Terrorism Casualties** — B.Tech capstone, Department of Data Science, MPSTME.

Text-mined a UN Attention Score from UN Official Document System reports and merged
it with Global Terrorism Database casualties and World Bank governance indicators
into a 1995–2020 country-year panel. Estimated pooled OLS, fixed effects, random
effects and two-step difference/System GMM to handle persistence and endogeneity.
Political stability holds a robust negative association with casualties; discourse
volume alone does not.

---

<a href="https://github.com/pr1tzy">
<img height="150" alt="stats" src="https://github-readme-stats.vercel.app/api?username=pr1tzy&show_icons=true&hide_border=true&hide_title=true&include_all_commits=true&bg_color=0b0a0f&text_color=8a8597&icon_color=7c5cff&title_color=4ad9d9&ring_color=7c5cff" />
<img height="150" alt="languages" src="https://github-readme-stats.vercel.app/api/top-langs/?username=pr1tzy&layout=compact&hide_border=true&hide_title=true&langs_count=8&bg_color=0b0a0f&text_color=8a8597&title_color=4ad9d9" />
</a>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/pr1tzy/pr1tzy/output/github-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/pr1tzy/pr1tzy/output/github-snake.svg" />
  <img alt="contribution graph" src="https://raw.githubusercontent.com/pr1tzy/pr1tzy/output/github-snake.svg" />
</picture>

---

`prithvi30singh@gmail.com` · `+91 9619952004` · [LinkedIn](https://linkedin.com/in/prithvi-singh-a796752bb) · [prithvisingh.fyi](https://prithvisingh.fyi)
