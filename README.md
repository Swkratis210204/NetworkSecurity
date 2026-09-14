# Network Security Project — Phishing Data Detection

An end-to-end ML pipeline that detects phishing/malicious network activity from tabular
feature data. It covers the full lifecycle: ingesting raw data from MongoDB, validating
and transforming it, training and evaluating multiple classifiers, tracking experiments
with MLflow (hosted on DagsHub), and serving predictions through a FastAPI app that's
built into a Docker image and deployed to an EC2 instance via GitHub Actions.

## Architecture

```
MongoDB (raw data)
      │
      ▼
Data Ingestion  →  Data Validation  →  Data Transformation  →  Model Trainer
      │                  │                     │                    │
      ▼                  ▼                     ▼                    ▼
 feature_store       drift_report        transformed data      trained model
                                          + preprocessor.pkl    + MLflow run
                                                                 (DagsHub)
```

All artifacts are written under a timestamped `Artifacts/` directory for each pipeline
run, and the final model/preprocessor are also synced to an S3 bucket.

## Pipeline stages (`networksecurity/components/`)

- **Data Ingestion** — pulls records from the `NetworkData` collection in MongoDB
  Atlas, exports to CSV, and splits into train/test sets.
- **Data Validation** — checks the incoming data against `data_schema/schema.yaml`
  and produces a drift report.
- **Data Transformation** — imputes missing values (KNN imputer) and produces the
  transformed train/test arrays plus a saved `preprocessing.pkl`.
- **Model Trainer** — trains and evaluates several classifiers (Logistic Regression,
  KNN, Decision Tree, Random Forest, AdaBoost, Gradient Boosting), logs metrics and
  the winning model to MLflow, and saves the final model artifact.

## API (`app.py`)

FastAPI app exposing:

| Route | Method | Description |
|---|---|---|
| `/` | GET | Redirects to `/docs` (Swagger UI) |
| `/train` | GET | Runs the full training pipeline end-to-end |
| `/predict` | POST | Upload a CSV, get predictions rendered as an HTML table |

## Environment variables

Create a `.env` file locally (never commit it) with:

```
MONGODB_URI=<mongodb+srv connection string>

MLFLOW_TRACKING_URI=https://dagshub.com/<user>/<repo>.mlflow
MLFLOW_TRACKING_USERNAME=<dagshub username>
MLFLOW_TRACKING_PASSWORD=<dagshub token>
```

AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`) are
picked up from the environment/AWS CLI config for S3 syncing of artifacts and models.

## Running locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

uvicorn app:app --reload
```

Visit `http://127.0.0.1:8000/docs` to try the API.

## Running with Docker

```bash
docker build -t networksecurity .
docker run -d -p 8080:8080 \
  -e MONGODB_URI=... \
  -e MLFLOW_TRACKING_URI=... \
  -e MLFLOW_TRACKING_USERNAME=... \
  -e MLFLOW_TRACKING_PASSWORD=... \
  -e AWS_ACCESS_KEY_ID=... \
  -e AWS_SECRET_ACCESS_KEY=... \
  -e AWS_REGION=... \
  networksecurity
```

The app listens on port `8080` inside the container.

## CI/CD (`.github/workflows/main.yml`)

Three jobs run on every push to `main`:

1. **Continuous Integration** — checkout, lint, unit tests (placeholder steps today).
2. **Continuous Delivery** — builds the Docker image and pushes it to Amazon ECR.
3. **Continuous Deployment** — runs on a **self-hosted runner** (an EC2 instance):
   pulls the latest image from ECR, stops/removes the previous container, and starts
   the new one on port `8080`.

### Required GitHub secrets

| Secret | Purpose |
|---|---|
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` | AWS auth for ECR/S3 |
| `AWS_ECR_LOGIN_URI` | ECR registry host only, e.g. `123456789012.dkr.ecr.us-east-1.amazonaws.com` (no repo name, no trailing slash) |
| `ECR_REPOSITORY_NAME` | Name of the ECR repository |
| `MONGODB_URI` | Passed into the running container |
| `MLFLOW_TRACKING_URI` / `MLFLOW_TRACKING_USERNAME` / `MLFLOW_TRACKING_PASSWORD` | Passed into the running container for MLflow/DagsHub tracking |

### Self-hosted runner setup

The deployment job needs an EC2 instance registered as a GitHub Actions self-hosted
runner (**Settings → Actions → Runners → New self-hosted runner**), with Docker
installed. Install the runner as a systemd service so it survives disconnects and
reboots:

```bash
cd actions-runner
sudo ./svc.sh install
sudo ./svc.sh start
```

The instance's security group must allow inbound TCP on port `8080` (and `22` for
SSH). Because Docker image layers accumulate on every deploy, the workflow runs
`docker system prune -a -f --volumes` after each deployment to avoid the instance
running out of disk space.

## Tech stack

Python · FastAPI · scikit-learn · MLflow (via DagsHub) · MongoDB Atlas · Docker ·
AWS (ECR, S3, EC2) · GitHub Actions
