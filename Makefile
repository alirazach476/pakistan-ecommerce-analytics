.PHONY: setup generate-data validate load dbt-run dbt-test dbt-docs pipeline test clean \
	docker-up docker-down docker-airflow export-excel insights dashboard powerbi pdf help

PYTHON ?= python
PIP ?= pip
DBT ?= dbt
COMPOSE ?= docker compose

help:
	@echo "Pakistan E-commerce Analytics Platform"
	@echo ""
	@echo "  make setup          Install Python deps and copy .env"
	@echo "  make generate-data  Generate synthetic Pakistani e-commerce data"
	@echo "  make validate       Validate raw CSV files"
	@echo "  make load           Load raw data into PostgreSQL"
	@echo "  make dbt-run        Run dbt models"
	@echo "  make dbt-test       Run dbt tests"
	@echo "  make dbt-docs       Generate dbt docs"
	@echo "  make pipeline       Full ETL: generate -> validate -> load -> dbt"
	@echo "  make export-excel   Export analytics summaries to Excel"
	@echo "  make insights       Generate business insights from warehouse"
	@echo "  make dashboard      Launch Streamlit BI dashboard (localhost:8501)"
	@echo "  make powerbi        Generate Power BI .pbip project"
	@echo "  make pdf            Generate project portfolio PDF"
	@echo "  make test           Run pytest"
	@echo "  make docker-up      Start PostgreSQL"
	@echo "  make docker-airflow Start PostgreSQL + Airflow"
	@echo "  make docker-down    Stop all containers"
	@echo "  make clean          Remove generated data and logs"

setup:
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example"; fi
	$(PIP) install -r requirements.txt
	@mkdir -p data/raw data/processed data/exports logs
	@echo "Setup complete. Edit .env with your credentials before running the pipeline."

generate-data:
	$(PYTHON) -m src.data_generation.generate

validate:
	$(PYTHON) -m src.validation.validate_raw

load:
	$(PYTHON) -m src.ingestion.pipeline

dbt-run:
	cd dbt && $(DBT) run --profiles-dir .

dbt-test:
	cd dbt && $(DBT) test --profiles-dir .

dbt-docs:
	cd dbt && $(DBT) docs generate --profiles-dir .

pipeline: generate-data validate load dbt-run dbt-test
	@echo "Full pipeline completed successfully."

export-excel:
	$(PYTHON) -m src.transformation.export_excel

insights:
	$(PYTHON) -m src.transformation.generate_insights

dashboard:
	$(PYTHON) -m streamlit run dashboards/streamlit/app.py

powerbi:
	$(PYTHON) scripts/generate_powerbi_project.py

pdf:
	$(PYTHON) scripts/generate_project_pdf.py

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

docker-up:
	$(COMPOSE) up -d postgres

docker-airflow:
	$(COMPOSE) --profile airflow up -d

docker-down:
	$(COMPOSE) --profile airflow --profile tools down

clean:
	rm -rf data/raw/*.csv data/raw/*.json data/processed/* data/exports/* logs/*.log
	@echo "Cleaned generated data and logs (kept directory structure)."
