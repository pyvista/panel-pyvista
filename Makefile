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

# Serve using the docker image but skip rebuilding if dependencies were built before
serve-docker:
	$(DOCKER) python /app/app.py
