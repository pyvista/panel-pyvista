IMAGE_NAME=app
GCP_PROJECT=reliable-fort-437922-m4
VERSION=latest

COMPOSE := docker compose
DOCKER_RUN := $(COMPOSE) run --rm --service-ports
DOCKER := $(DOCKER_RUN) app

guard-%: GUARD
	@ if [ -z '${${*}}' ]; then echo 'Environment variable $* not set.' && exit 1; fi

.PHONY: GUARD
GUARD:

build:
	$(COMPOSE) build --no-cache

bash:
	$(DOCKER) bash

shell:
	$(DOCKER) ipython

compile-requirements:
	pip-compile --output-file requirements.txt requirements.in -v

serve:
	panel serve app/app.py --allow-websocket-origin='*' --port 8080

serve-docker:
	$(DOCKER)
