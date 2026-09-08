# energy-data-platform

Pipeline de données de consommation et de production électrique française, de l'extraction d'un fichier CSV brut jusqu'à une API exposée en production sur Google Cloud Run.

## Sommaire

- [Source des données](#source-des-données)
- [Échantillon de travail](#échantillon-de-travail)
- [Colonnes](#colonnes)
- [Architecture](#architecture)
- [Pipeline Python](#pipeline-python-extract--transform--validate)
- [BigQuery, staging et MERGE](#bigquery-staging-et-merge)
- [Modélisation dbt](#modélisation-dbt)
- [Orchestration Airflow](#orchestration-airflow)
- [API FastAPI](#api-fastapi)
- [Docker](#docker)
- [Cloud Run](#cloud-run)
- [Cloud Scheduler](#cloud-scheduler)
- [Tests](#tests)
- [Lancer le projet en local](#lancer-le-projet-en-local)
- [Limites du projet](#limites-du-projet)

## Source des données

Les données proviennent de **RTE** (Réseau de Transport d'Électricité), via le fichier `eco2mix-regional-cons-def.csv` : consommation et production électrique régionale, au pas demi-horaire, séparateur `;`.

## Échantillon de travail

Le pipeline travaille sur un sous-ensemble du fichier brut :

- année **2024** uniquement ;
- deux régions : **Île-de-France** et **Hauts-de-France** ;
- période couverte : `2024-01-01 00:00:00` → `2024-12-31 23:30:00`.

Avant déduplication : **35 136 lignes**, 4 doublons sur la clé `(Timestamp, Region)`.
Après déduplication : **35 132 lignes**, 0 doublon.

## Colonnes

Mapping du CSV source (français) vers les noms utilisés dans tout le projet :

| Colonne source (CSV) | Colonne Python |
|---|---|
| `Date - Heure` | `Timestamp` |
| `Région` | `Region` |
| `Consommation (MW)` | `Consumption` |
| `Thermique (MW)` | `Thermal` |
| `Nucléaire (MW)` | `Nuclear` |
| `Eolien (MW)` | `Wind` |
| `Solaire (MW)` | `Solar` |
| `Hydraulique (MW)` | `Hydro` |
| `Bioénergies (MW)` | `Bioenergy` |

Colonnes métier calculées : `Total_Production`, `Renewable_production`, `Renewable_Share`.

## Architecture

```
CSV RTE brut
    ↓
extract.py
    ↓
transform.py
    ↓
validate.py
    ↓
BigQuery staging
    ↓
MERGE vers table clean
    ↓
dbt staging
    ↓
dbt mart quotidien (daily_region_summary)
    ↓
FastAPI
    ↓
Cloud Run
```

Airflow orchestre l'enchaînement pipeline + dbt. Cloud Scheduler déclenche l'endpoint interne en production.

```
energy-data-platform/
├── airflow/dags/energy_pipeline.py
├── api/
│   ├── main.py
│   ├── repository.py
│   ├── service.py
│   └── static/          # interface web (index.html)
├── data/
│   ├── raw/             # non inclus dans le git
│   ├── sample/
│   └── tests/
├── dbt_energy/
│   └── models/
│       ├── staging/
│       └── marts/
├── docker/Dockerfile
├── src/
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load_bigquery.py
│   └── pipeline.py
└── tests/
```

## Pipeline Python (extract / transform / validate)

- **`extract.py`** : lit le CSV brut, filtre l'échantillon (année + régions), sauvegarde un CSV de travail.
- **`transform.py`** : sélectionne et renomme les colonnes, convertit les types (dates, numériques), supprime les doublons sur `(Timestamp, Region)`, calcule les colonnes métier (`Total_Production`, `Renewable_production`, `Renewable_Share`).
- **`validate.py`** : contrôle qualité sans modification des données — colonnes manquantes, doublons résiduels, taux de valeurs nulles, valeurs numériques incohérentes (consommation négative, part renouvelable hors `[0, 1]`). `validate_or_raise()` bloque le pipeline si un problème est jugé critique.

Principe : **transformer** change les données pour qu'elles soient bonnes puis **valider** vérifie qu'elles le sont vraiment.

## BigQuery, staging et MERGE

Le chargement est **idempotent** : les nouvelles données sont d'abord chargées dans une table de staging temporaire, puis fusionnées vers la table finale via une instruction `MERGE` SQL, sur la clé `(Timestamp, Region)`. Relancer le pipeline plusieurs fois sur les mêmes données ne crée jamais de doublons — vérifié en conditions réelles lors de la mise en place de Cloud Scheduler.

## Modélisation dbt

- **Staging** (`stg_energy`) : nettoyage minimal, pas de logique métier.
- **Mart** (`daily_region_summary`) : une ligne par jour et par région, avec consommation moyenne/max, production totale, production renouvelable et part renouvelable moyenne.
- Tests dbt : `not_null`, `unique` (combinaison `Date` + `Region`), `accepted_values` sur les régions.

## Orchestration Airflow

DAG `energy_pipeline` (Docker Compose, local) : `check_file → run_pipeline → dbt_run → dbt_test`. Retries configurés, `catchup=False`.

## API FastAPI

Routes exposées (mart `daily_region_summary`, sauf `/health` et `/internal/run-pipeline`) :

| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | Vérifie que l'API répond |
| GET | `/regions` | Liste les régions disponibles |
| GET | `/summary/{region}` | Résumé journalier (consommation, production, part renouvelable) |
| GET | `/summary/{region}/anomalies` | Jours où la consommation dévie fortement de la moyenne (méthode écart-type, seuil 2σ) |
| GET | `/regions/compare` | Classement des régions par part renouvelable moyenne |
| GET | `/summary/{region}/trend` | Tendance de consommation (hausse / baisse / stable) |
| POST | `/internal/run-pipeline` | Déclenche une exécution complète du pipeline (appelé par Cloud Scheduler) |

Une interface web minimaliste (`/ui`) permet de tester l'ensemble de ces endpoints depuis un navigateur, sans passer par Swagger ou Postman — formulaires, résultats en JSON.

## Docker

Image basée sur `python:3.11-slim`, exécute l'API via Uvicorn sur le port `8080`. Construite et poussée vers **Artifact Registry** (`europe-west9`).

## Cloud Run

L'API est déployée sur **Cloud Run**, hébergement conteneurisé qui scale automatiquement à zéro instance en l'absence de trafic. La configuration (`GCP_PROJECT_ID`, `BQ_DATASET_ID`, etc.) est injectée via des variables d'environnement — jamais codée en dur (voir [Limites](#limites-du-projet)).

Le compte de service Cloud Run dispose des rôles IAM `BigQuery Data Viewer` et `BigQuery Job User`, nécessaires pour que l'API lise le mart en production.

## Cloud Scheduler

Une tâche planifiée (`energy-monthly-run`) appelle `POST /internal/run-pipeline` une fois par mois, démontrant l'automatisation du déclenchement en production sans faire tourner Airflow en continu dans le cloud. Voir [Limites](#limites-du-projet) pour une note sur la pertinence réelle de cette fréquence sur ce projet.

## Tests

```bash
pytest --ignore=tests/test_airflow_dag.py
```

`test_airflow_dag.py` s'exécute uniquement à l'intérieur du conteneur Airflow (Airflow n'est pas nativement supporté sous Windows mais a tout de même été correctement testé de mon côté) :

```bash
docker compose exec -u root airflow-scheduler python -m pip install pytest
docker compose cp ../tests/test_airflow_dag.py airflow-scheduler:/tmp/test_airflow_dag.py
docker compose exec airflow-scheduler python -m pytest /tmp/test_airflow_dag.py
```

Les fonctions d'extraction et de transformation sont testées avec les vraies valeurs du CSV source. Les tests de validation combinent données réelles et cas limites fabriqués volontairement (valeurs nulles, négatives) pour couvrir les scénarios d'erreur. Les couches service et infrastructure (API, BigQuery) sont testées avec des mocks et des données de synthèse, conformément à la pratique standard pour ce type de code.

## Lancer le projet en local

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8080
```

Puis ouvrir `http://127.0.0.1:8080/ui`.

## Limites du projet

- **Gestion de la configuration** : les variables sensibles (`GCP_PROJECT_ID`, `BQ_DATASET_ID`, etc.) sont injectées via des fichiers `.env`, jamais codées en dur, conformément au principe des *12-factor apps*. Limite connue : ces valeurs sont dupliquées entre deux fichiers `.env` distincts (local et Airflow) plutôt que centralisées dans une source unique. En production, un gestionnaire de secrets (GCP Secret Manager) ou un fichier `.env` partagé entre les deux services serait préférable.
- **Traitement en mémoire complète** : le pipeline charge l'intégralité du CSV en mémoire avec Pandas plutôt que de le traiter par lots (*chunks*). Sur ce projet (~450 Mo), cela a nécessité de porter la mémoire allouée à Cloud Run à 4 Gi. Cette approche ne passerait pas à l'échelle sur un volume de données significativement plus important. La bonne pratique pour un volume plus important serait de traiter le fichier par lots avec le paramètre `chunksize` de Pandas (`pd.read_csv(..., chunksize=10000)`) : chaque lot est transformé et écrit indépendamment, ce qui garde une empreinte mémoire stable et prévisible quelle que soit la taille du fichier source, plutôt qu'un pic proportionnel à sa taille totale.
- **Cloud Scheduler sur données figées** : le dataset source est un instantané figé (année 2024, jamais mis à jour). Une exécution mensuelle automatique du pipeline n'a donc pas d'utilité fonctionnelle réelle ici — le `MERGE` idempotent garantit simplement qu'aucune donnée n'est dupliquée. La tâche a été mise en place pour démontrer la maîtrise du mécanisme (découplage planification / orchestration), pas pour répondre à un besoin métier réel sur ce projet précis.
- **Pas de couche frontend riche** : l'interface `/ui` est volontairement minimaliste (HTML/CSS/JS sans framework), pensée pour tester l'API plutôt que pour être un outil de visualisation avancé.
- **Airflow non testable nativement sous Windows** : nécessite Docker Compose et une exécution des tests à l'intérieur du conteneur (voir section Tests).