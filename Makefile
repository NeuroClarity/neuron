.DEFAULT_GOAL := help
APP?=neuron
COMMIT_SHA?=$(shell git rev-list HEAD --max-count=1 --abbrev-commit)
REGISTRY_REPO?=471943556279.dkr.ecr.us-west-2.amazonaws.com
LOG_FILE_NAME?=./logs/$(shell date +%Y%m%d_%H%M%S)_$(APP).log

OK_COLOR=\033[32;01m
NO_COLOR=\033[0m
ERROR_COLOR=\033[31;01m
WARN_COLOR=\033[33;01m

docker-build: 
		docker build -t ${APP} .
		docker tag ${APP} ${APP}:${COMMIT_SHA}
		docker tag ${APP}:${COMMIT_SHA} ${REGISTRY_REPO}/${APP}:${COMMIT_SHA}

docker-push:
		docker push ${REGISTRY_REPO}/${APP}:${COMMIT_SHA}

ecr-login:
		@echo "Logging in to ECR..."
		@$$(aws ecr get-login --no-include-email)

docker-build-and-push: ecr-login docker-build docker-push
