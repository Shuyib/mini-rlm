# Thank you @Earthly https://www.youtube.com/watch?v=w2UeLF7EEwk
# Can be adapted to pipenv, and poetry
# Other languages coming soon especially R and Julia

# .ONESHELL tells make to run each recipe line in a single shell
.ONESHELL:

# .DEFAULT_GOAL tells make which target to run when no target is specified
.DEFAULT_GOAL := all

# Specify python location in virtual environment
# Specify pip location in virtual environment
PYTHON := .venv/bin/python3
PIP := .venv/bin/pip3
NBDEV_BIN := .venv/bin
DOCKER_IMAGE_NAME := test_app
DOCKER_IMAGE_VERSION := v0.0.0
DOCKER_IMAGE_TAG := $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION)

#-----------------------------------------------------------------
# Package Manager Detection
#-----------------------------------------------------------------

# Detect available package managers
# UV https://app.readytensor.ai/publications/uv-package-1yiSfLXTffSF?utm_id=12
DETECT_PIPENV := $(shell which pipenv)
DETECT_POETRY := $(shell which poetry)
DETECT_UV     := $(shell which uv)

# Set flags (1: available, 0: not available)
ifeq ($(DETECT_PIPENV),)
  HAS_PIPENV := 0
else
  HAS_PIPENV := 1
endif

ifeq ($(DETECT_POETRY),)
  HAS_POETRY := 0
else
  HAS_POETRY := 1
endif

ifeq ($(DETECT_UV),)
  HAS_UV := 0
else
  HAS_UV := 1
endif

#-----------------------------------------------------------------
# Default Package Manager Selection (priority: uv > pipenv > poetry)
#-----------------------------------------------------------------

ifeq ($(HAS_UV),1)
  PACKAGE_MANAGER := uv
else ifeq ($(HAS_PIPENV),1)
  PACKAGE_MANAGER := pipenv
else ifeq ($(HAS_POETRY),1)
  PACKAGE_MANAGER := poetry
else
  $(error No supported package manager found (pipenv, poetry, or uv))
endif

#-----------------------------------------------------------------
# Set Commands Based on the Package Manager
#-----------------------------------------------------------------

ifeq ($(PACKAGE_MANAGER),pipenv)
  INSTALL_COMMAND := pipenv install --dev
  RUN_COMMAND     := pipenv run
else ifeq ($(PACKAGE_MANAGER),poetry)
  INSTALL_COMMAND := poetry install
  RUN_COMMAND     := poetry run
else ifeq ($(PACKAGE_MANAGER),uv)
  INSTALL_COMMAND := uv pip install -e . -r requirements-dev.txt
  RUN_COMMAND     := python  # or python3, depending on your setup
endif

detect:
    @echo "Pipenv detected: $(HAS_PIPENV)"
    @echo "Poetry detected: $(HAS_POETRY)"
    @echo "UV detected: $(HAS_UV)"
	@echo "Package manager selected: $(PACKAGE_MANAGER)"


venv/bin/activate: requirements.txt
	# create virtual environment
	python3 -m venv .venv
	# make command executable
	chmod +x .venv/bin/activate
	# activate virtual environment
	. .venv/bin/activate

activate:
	# Print instructions for activating the virtual environment
	@echo "To activate the virtual environment, run the following command in your terminal:"
	@echo "source .venv/bin/activate"

install: venv/bin/activate requirements.txt # prerequisite
	# install commands
	$(PIP) --no-cache-dir install --upgrade pip &&\
		$(PIP) --no-cache-dir install -r requirements.txt &&\
		$(PIP) --no-cache-dir install --upgrade ruff

nbdev-install: venv/bin/activate requirements.txt
	# install nbdev as an optional notebook-first workflow
	$(PIP) --no-cache-dir install --upgrade nbdev

nbdev-init: nbdev-install
	# create settings.ini and GitHub workflow scaffolding
	@if [ -f settings.ini ]; then \
		echo "settings.ini already exists; nbdev is already initialized."; \
	else \
		$(NBDEV_BIN)/nbdev-new; \
	fi

nbdev-hooks: nbdev-install
	# strip notebook metadata before commits to reduce merge conflicts
	$(NBDEV_BIN)/nbdev-install-hooks

nbdev-export: nbdev-install
	# export #|export cells into Python modules
	$(NBDEV_BIN)/nbdev-export

nbdev-preview: nbdev-install
	# preview the generated documentation site locally
	$(NBDEV_BIN)/nbdev-preview

nbdev-test: nbdev-install
	# run notebook-based tests
	$(NBDEV_BIN)/nbdev-test

nbdev-clean: nbdev-install
	# clean notebook metadata to keep git diffs small
	$(NBDEV_BIN)/nbdev-clean

nbdev-help: nbdev-install
	# show the available nbdev commands
	$(NBDEV_BIN)/nbdev-help

nbdev-prepare: nbdev-install
	# bundle export, test, and clean before pushing
	$(NBDEV_BIN)/nbdev-prepare

nbdev-pypi: nbdev-install
	# publish the package to PyPI and bump the version
	$(NBDEV_BIN)/nbdev-pypi

nbdev-conda: nbdev-install
	# build and publish the conda package
	$(NBDEV_BIN)/nbdev-conda

nbdev-release: nbdev-install
	# run the full release flow for PyPI and Conda
	$(NBDEV_BIN)/nbdev-release

ruff-install: activate
	# ensure Ruff linter is available
	$(PIP) --no-cache-dir install --upgrade ruff

docstring: activate
	# format docstring
	pyment -w -o numpydoc *.py

format: activate
	# format code
	black *.py utils/*.py testing/*.py

clean:
	# clean directory of cache
	rm -rf __pycache__ &&\
	rm -rf utils/__pycache__ &&\
	rm -rf testing/__pycache__ &&\
	rm -rf .pytest_cache &&\
	rm -rf .venv

lint: activate install format ruff-install
	# flake8 or #pylint
	$(PYTHON) -m ruff check . &&\
	pylint --disable=R,C --errors-only *.py utils/*.py testing/*.py

ruff: activate install ruff-install
	# run Ruff lint checks
	$(PYTHON) -m ruff check .

ruff-fix: activate install ruff-install
	# run Ruff with autofix enabled
	$(PYTHON) -m ruff check --fix .

setup_readme:  ## Create a README.md
	@if [ ! -f README.md ]; then \
		echo "# Project Name\n\
Description of the project.\n\n\
## Installation\n\
- Step 1\n\
- Step 2\n\n\
## Usage\n\
Explain how to use the project here.\n\n\
## Contributing\n\
Explain how to contribute to the project.\n\n\
## License\n\
License information." > README.md; \
		echo "README.md created."; \
	else \
		echo "README.md already exists."; \
	fi

test: activate install format
	# test
	$(PYTHON) -m pytest testing/*.py

run: activate install format lint
	# run application
  	# example $(PYTHON) app.py

review-code:
	@echo "#### General Code Review Prompt ####"
	@echo "1. Code Quality:"
	@echo "   - Architecture patterns"
	@echo "   - Design principles (SOLID, DRY, KISS)"
	@echo "   - Code complexity"
	@echo "   - Documentation quality"

	@echo "2. Reliability:"
	@echo "   - Single and multiple points of failure"
	@echo "   - Failover strategies"
	@echo "   - Resource management"
	@echo "   - Thread safety"

	@echo "3. Performance:"
	@echo "   - Algorithmic efficiency"
	@echo "   - Memory usage"
	@echo "   - I/O operations"
	@echo "   - Caching strategy"

review-ds:
	@echo "#### Data Science Review Prompt ####"
	@echo "1. Data Pipeline:"
	@echo "   - Data validation (schema, types, ranges)"
	@echo "   - Preprocessing steps (scaling, encoding, imputation)"
	@echo "   - Feature engineering (relevance, creation, selection)"
	@echo "   - Data versioning (tracking datasets)"
	@echo "   - Data leakage checks"
	@echo "   - Handling of missing or anomalous data"

	@echo "2. Model Development:"
	@echo "   - Algorithm selection rationale"
	@echo "   - Hyperparameter tuning methodology and tracking"
	@echo "   - Cross-validation strategy (appropriateness, implementation)"
	@echo "   - Choice of evaluation metrics (relevance to business goal)"
	@echo "   - Model interpretability/explainability methods"
	@echo "   - Bias and fairness assessment"
	@echo "   - Model persistence (saving/loading)"
	@echo "   - Code reproducibility (seeds, dependencies)"

	@echo "3. Production Readiness:"
	@echo "   - Scalability of prediction/inference code"
	@echo "   - Monitoring setup (technical and model performance metrics)"
	@echo "   - Logging for model inputs/outputs/errors"
	@echo "   - A/B testing or canary deployment capability"
	@echo "   - Model deployment pipeline (automation)"
	@echo "   - Rollback strategy for model updates"

	@echo "4. Experiment Tracking:"
	@echo "   - Are experiments logged (parameters, code versions, metrics)?"
	@echo "   - Is an experiment tracking tool used (e.g., MLflow, W&B)?"
	@echo "   - Are model artifacts versioned and stored?"

review-logging:
	@echo "#### Logging Review Prompt ####"
	@echo ""
	@echo "1. Level 1: Print Statements"
	@echo "   - Are there raw print() statements used for debugging?"
	@echo "   - Should these be replaced with proper logging?"
	@echo "   - Are any critical error conditions only visible via print statements?"
	@echo ""
	@echo "2. Level 2: Logging Libraries"
	@echo "   - Is a proper logging library being used consistently?"
	@echo "   - Are appropriate log levels (DEBUG, INFO, WARNING, ERROR) used?"
	@echo "   - Is logging properly configured (handlers, formatters)?"
	@echo "   - Are logs structured (JSON/key-value) for better analysis?"
	@echo "   - Is sensitive information protected from being logged?"
	@echo ""
	@echo "3. Level 3: Tracing"
	@echo "   - Is function/method entry/exit tracked for performance analysis?"
	@echo "   - Are execution paths through the code captured with timing data?"
	@echo "   - Are trace IDs used to track request flow?"
	@echo ""
	@echo "4. Level 4: Distributed Tracing"
	@echo "   - Is context propagated across service boundaries?"
	@echo "   - Are trace IDs maintained throughout the entire request lifecycle?"
	@echo "   - Is sampling strategy appropriate for production load?"
	@echo ""
	@echo "5. Level 5: Observability"
	@echo "   - Are logs, metrics, and traces integrated into a unified system?"
	@echo "   - Is there anomaly detection for unexpected behaviors?"
	@echo "   - Does the system provide business-level insights from technical data?"
	@echo "   - Is the observability stack scalable for production use?"

docker_build: Dockerfile
	# build container. Feel freee to change the platform given your needs
	# docker build --platform linux/amd64 -t plot-timeseries-app:v0 .
	# podman build --platform linux/amd64 -t plot-timeseries-app:v0 .

docker_run_test: Dockerfile
	# linting Dockerfile
	# podman run --rm -i hadolint/hadolint < Dockerfile
	docker run --rm -i hadolint/hadolint < Dockerfile

docker_clean: Dockerfile
	# remove dangling images, containers, volumes and networks
	# podman system prune -a
	docker system prune -a

docker_run: Dockerfile docker_build
	# run docker
	# # podman run --platform linux/amd64-e ENDPOINT_URL -e SECRET_KEY -e SPACES_ID -e SPACES_NAME plot-timeseries-app:v0
	# docker run --platform linux/amd64 -e ENDPOINT_URL -e SECRET_KEY -e SPACES_ID -e SPACES_NAME plot-timeseries-app:v0
	

docker_image_size:
	# Show the size of the Docker image
	@echo "Image size for $(DOCKER_IMAGE_TAG):"
	@docker image ls $(DOCKER_IMAGE_TAG) --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"

docker_image_history:
	# Show the layer history for the Docker image
	@echo "Layer history for $(DOCKER_IMAGE_TAG):"

docker_push: docker_build
	# push to registry
	# docker tag <my-image> registry.digitalocean.com/<my-registry>/<my-image>
	# docker push registry.digitalocean.com/<my-registry>/<my-image>
	# podman tag <my-image> registry.digitalocean.com/<my-registry>/<my-image>
	# podman push registry.digitalocean.com/<my-registry>/<my-image>

#-----------------------------------------------------------------
# Agent/Skill/Prompt template helpers
#-----------------------------------------------------------------

list-variants:
	@echo "Recognized filename variants:"
	@echo "  - AGENTS.md / agents.md"
	@echo "  - SKILL.md / skills.md / SKILL.md"
	@echo "  - <name>.agent.md"
	@echo "  - <name>.skill.md"
	@echo "  - <name>.instructions.md"
	@echo "  - <name>.prompt.md"
	@echo "  - copilot-instructions.md"

show-template:
	@echo "Available templates (use NAME=agent|skill|prompt):"
	@if [ -z "$(NAME)" ]; then \
		echo "Specify NAME=agent|skill|prompt"; exit 1; \
	fi; \
	if [ "$(NAME)" = "agent" ]; then \
		cat <<'AGENT_TEMPLATE'; \
	# Agent: {{name}}
	# Purpose: Short description of the agent and its responsibilities.

	## Metadata
	- name: <agent-name>
	- owner: <owner>
	- purpose: Describe what this agent does in one line

	## Behavior / Instructions
	- Summary of high-level behavior and limits.

	## Tools / Skills
	- skills: |
		- skill-name: brief description

	## Usage examples
	- Example: `make new NAME=my-agent TYPE=agent`

	## Explanation
	This template describes a high-level agent: its metadata, responsibilities,
	and the skills it uses. Fill `name`, `owner`, and `purpose`, then list the
	skills the agent will call. Use `make new NAME=<your-name> TYPE=agent` to
	generate a file from this template in the repo root. Edit the generated
	file to add implementation notes, runbooks, or links to code that implements
	the agent.

	AGENT_TEMPLATE
	elif [ "$(NAME)" = "skill" ]; then \
		cat <<'SKILL_TEMPLATE'; \
	# SKILL.md - Skill description and integration notes

	## Purpose
	Describe the capability this skill provides.

	## Interface
	- Inputs: list and types
	- Outputs: list and types

	## Files
	- Suggested location: <repo>/skills/<skill-name>/SKILL.md

	## Example
	- Invoke pattern or CLI example

	## Explanation
	Document what the skill does, the expected inputs/outputs, and any
	preconditions. Include examples of common invocations and links to code
	or tests that exercise the skill. Use `make new NAME=<your-name> TYPE=skill`
	to create a file from this template.

	SKILL_TEMPLATE
	elif [ "$(NAME)" = "prompt" ]; then \
		cat <<'PROMPT_TEMPLATE'; \
	# Prompt template: Title

	## Description
	Short description of what this prompt/task does.

	## Template
	<Provide the reusable prompt template here.>

	## Explanation
	Explain intended use of this prompt, expected inputs, how to adapt it for
	other tasks, and safety/guardrail notes. Use `make new NAME=<your-name> TYPE=prompt`
	to create a file from this prompt template.

	PROMPT_TEMPLATE
	else \
		echo "Unknown template: $(NAME)"; exit 1; \
	fi

new:
	@echo "Creating a new file from template. Usage: make new NAME=foo TYPE=agent|skill|prompt"; \
	@if [ -z "$(NAME)" ] || [ -z "$(TYPE)" ]; then \
		echo "Usage: make new NAME=foo TYPE=agent|skill|prompt"; exit 1; \
	fi; \
	case "$(TYPE)" in \
		agent) FILE="$(NAME).agent.md";; \
		skill) FILE="$(NAME).skill.md";; \
		prompt) FILE="$(NAME).prompt.md";; \
		*) echo "Unknown TYPE: $(TYPE)"; exit 1;; \
	esac; \
	if [ -f "$$FILE" ]; then echo "$$FILE already exists"; exit 1; fi; \
	make show-template NAME=$(TYPE) > "$$FILE"; echo "Created $$FILE"


docs:
	@echo "Conventions and further reading:"
	@echo "  - See Notes.md for internal conventions"
	@echo "  - See TODO.md for outstanding tasks"
	@echo "  - Markdown usage: https://www.markdownguide.org"
	@echo "  - Agent/Skill concepts: see your project Notes.md and general design patterns"
	@echo "agents.md best practices can be found here: https://developers.openai.com/api/docs/guides/agents"
	@echo "skills.md best practices can be found here: https://developers.openai.com/api/docs/guides/tools-skills"
	@echo "copilot-instructions.md best practices can be found here: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions?versionId=free-pro-team%40latest&productId=copilot"
	@echo "When to use agents.md: list and describe higher-level agents that orchestrate workflows. Examples: automation agent, research assistant, multi-step orchestration."
	@echo "When to use skills.md: document reusable capabilities or connectors. Examples: search skill, DB access, code-execution skill, API wrappers."
	@echo "When to use copilot-instructions.md: define workspace assistant behavior and coding conventions. Examples: repo style rules, review prompts, secret-handling guidance."


help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  detect          Detect package managers"
	@echo "  activate        Activate virtual environment"
	@echo "  install         Install dependencies"
	@echo "  docstring       Format docstrings"
	@echo "  format          Format code"
	@echo "  clean           Clean directory of cache"
	@echo "  lint            Lint code"
	@echo "  ruff            Run Ruff lint checks"
	@echo "  ruff-fix        Run Ruff lint checks with autofix"
	@echo "  test            Run tests"
	@echo "  run             Run application"
	@echo "  nbdev-install   Install nbdev into the virtual environment"
	@echo "  nbdev-init      Run nbdev_new and create settings.ini/workflows"
	@echo "  nbdev-hooks     Install git hooks that clean notebook metadata"
	@echo "  nbdev-export    Export notebooks to Python modules"
	@echo "  nbdev-preview   Preview the documentation site locally"
	@echo "  nbdev-test      Run notebook-based tests"
	@echo "  nbdev-clean     Clean notebook metadata"
	@echo "  nbdev-help      Show nbdev CLI help"
	@echo "  nbdev-prepare   Run nbdev export, test, and clean"
	@echo "  nbdev-pypi      Publish the package to PyPI"
	@echo "  nbdev-conda     Publish the package to Conda"
	@echo "  nbdev-release   Run the full nbdev release flow"
	@echo "  setup_readme    Create a README.md"
	@echo "  review-code     Code review prompt"
	@echo "  review-ds       Data Science review prompt"
	@echo "  review-logging  Logging implementation review prompt"
	@echo "  docker-build    Build Docker image $(DOCKER_IMAGE_TAG)"
	@echo "  docker_run_test Lint Dockerfile"
	@echo "  docker_clean    Remove dangling images, containers, volumes, and networks"
	@echo "  docker_run      Run Docker container"
	@echo "  docker_push     Push Docker container to registry"
	@echo "  list-variants   Show recognized agent/skill/prompt filename variants"
	@echo "  show-template   Print an embedded template (use NAME=agent|skill|prompt)"
	@echo "  help            Show this help message"

# .PHONY tells make that these targets do not represent actual files
.PHONY: activate format clean lint test build run install ruff ruff-fix ruff-install nbdev-install nbdev-init nbdev-hooks nbdev-export nbdev-preview nbdev-test nbdev-clean nbdev-help nbdev-prepare nbdev-pypi nbdev-conda nbdev-release docker_build docker_run docker_push docker_clean docker_run_test list-variants show-template new docs init-templates search-templates

all: install format lint test run docker_build docker_run docker_push
