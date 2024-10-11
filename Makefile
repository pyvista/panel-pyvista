COMPOSE := docker compose
DOCKER_RUN := $(COMPOSE) run --rm --service-ports
DOCKER := $(DOCKER_RUN) app-dev

guard-%: GUARD
	@ if [ -z '${${*}}' ]; then echo 'Environment variable $* not set.' && exit 1; fi

.PHONY: GUARD
GUARD:

compile-requirements:
	pip-compile --output-file app/requirements.txt app/requirements.in -v

# Build only the dependencies stage
build:
	$(COMPOSE) build --no-cache

bash:
	$(DOCKER) bash

shell:
	$(DOCKER) python

serve:
	python app/app.py

# Serve using the docker image
serve-docker:
	$(DOCKER) python /app/app.py

deploy:
	gcloud run deploy pyvista-demo --source $(shell pwd) \
    --cpu=1 \
    --memory=1Gi \
    --allow-unauthenticated \
    --min-instances=1 \
    --max-instances=1 \
    --port=8080 \
    --timeout=3600 \
    --region=us-central1
# --service-account='YOUR-SERVICE-ACCOUNT'
