# mini_rlm

Recursive Language Model utilities extracted from a notebook-first workflow using nbdev.

## Description

This repository provides the `mini_rlm` package with REPL-based tracing helpers and utilities (`RLM`, `rlm`, `run_repl`, etc.). The source of truth is the notebook `nbs/rlm_lisette_v2.ipynb` and exports are generated to `mini_rlm/` via `nbdev`.

## Installation

Recommended: create a virtual environment and install requirements.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make nbdev-install
```

## Usage

- Export notebook code into package modules:

```bash
make nbdev-export
```

- Run notebook-based tests and prepare docs:

```bash
make nbdev-prepare
```

## Contributing

Please open issues or PRs. Before contributing, run `make lint` and `make test`.

## License

Apache Software License 2.0

## API Keys / Configuration

This project uses OpenRouter for LLM requests in some demo paths. You must provide an API key to use those features locally and for CI.

- Locally (example):

```bash
export OPENROUTER_API_KEY="sk-..."
```

- For GitHub Actions (CI): add a repository secret named `OPENROUTER_API_KEY` in the repository Settings → Secrets and variables → Actions.

If you do not provide a key, features that make live LLM requests will fail — however most functionality can still be used offline or with mocked inputs.

