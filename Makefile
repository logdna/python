# Makefile Version 2021032403
#
# Source in repository specific environment variables
include .config.mk

# Define commands via docker
DOCKER = docker
DOCKER_RUN := $(DOCKER) run --rm -i
WORKDIR :=/workdir
DOCKER_COMMAND := $(DOCKER_RUN) -v $(PWD):$(WORKDIR):Z -w $(WORKDIR) \
	-e XDG_CONFIG_HOME=$(WORKDIR) \
	-e XDG_CACHE_HOME=$(WORKDIR) \
	-e POETRY_CACHE_DIR=$(WORKDIR)/.cache \
	-e POETRY_VIRTUALENV_IN_PROJECT=true \
	-e PYPI_TOKEN \
	-e GH_TOKEN \
	-e GIT_AUTHOR_NAME \
	-e GIT_AUTHOR_EMAIL \
	-e GIT_COMMITTER_NAME \
	-e GIT_COMMITTER_EMAIL \
	us.gcr.io/logdna-k8s/python:3.7-ci

POETRY_COMMAND := $(DOCKER_COMMAND) poetry

# Exports the variables for shell use
export

# This helper function makes debugging much easier.
.PHONY:debug-%
debug-%: ## Debug a variable by calling `make debug-VARIABLE`
	@echo $(*) = $($(*))

.PHONY:help
.SILENT:help
help: ## Show this help, includes list of all actions.
	@awk 'BEGIN {FS = ":.*?## "}; /^.+: .*?## / && !/awk/ {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' ${MAKEFILE_LIST}

.PHONY:clean
clean: ## purge build time artifacts
	rm -rf dist/ build/ coverage/ pypoetry/ pip/ .cache

.PHONY:changelog
changelog: ## print the next version of the change log to stdout
	$(POETRY_COMMAND) run semantic-release changelog --unreleased

.PHONY:install
install: ## install development and build time dependencies
	$(POETRY_COMMAND) install --no-interaction -vvv

.PHONY:lint
lint: ## run lint rules and print error report
	$(POETRY_COMMAND) run task lint

.PHONY:lint-fix
lint-fix:## attempt to auto fix linting error and report remaining errors
	$(POETRY_COMMAND) run task lint:fix

.PHONY:package
package: ## Generate a python sdist and wheel
	$(POETRY_COMMAND) build

.PHONY:release
release: clean install ## run semantic release build and publish results to github + pypi based on unreleased commits
	$(POETRY_COMMAND) run task release

.PHONY:release-dry
release-dry: clean install changelog ## run semantic release in noop mode
	$(POETRY_COMMAND) run semantic-release publish --noop --verbosity=DEBUG

.PHONY:release-patch
release-patch: clean install ## run semantic release build and force a patch release
	$(POETRY_COMMAND) run semantic-release publish --patch

.PHONY:release-minor
release-minor: clean install                    ## run semantic release build and force a minor release
	$(POETRY_COMMAND) run semantic-release publish --minor

.PHONY:release-major
release-major: clean install                    ## run semantic release build and force a major release
	$(POETRY_COMMAND) run semantic-release publish --major

.PHONY:test
test:                            ## run project test suite
	$(POETRY_COMMAND) run task test

