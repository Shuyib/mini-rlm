# Packaging with nbdev — TODO

This TODO documents the minimal steps to prepare and build a package from notebooks using `nbdev`.

1. Prepare metadata
   - Create or edit `settings.ini` at repo root with project metadata (see example below).
   - Ensure `lib_path` matches the package folder you want (e.g., `mini_rlm`).

2. Mark exportable code in notebooks
   - In `rlm_lisette_v2.ipynb`, add `#| export` as the first line of every code cell you want exported.
   - Keep tests, experiments, and scratch cells unmarked.

3. Confirm package layout * (start here next time)
   - Ensure a package folder exists matching `lib_path` (create `mini_rlm/__init__.py` if needed).
   - Add runtime deps to `requirements.txt` (e.g., `fastcore`, `ipython`, `litellm`, `tiktoken`, `toolslm`, `rich`).

4. Create and activate venv (Makefile targets available)
   - Create the virtual env:

     ```bash
     make venv/bin/activate
     source .venv/bin/activate
     ```

5. Install nbdev and dev deps
   - Install into the venv:

     ```bash
     make nbdev-install
     ```

6. Initialize nbdev (if not already)
   - If you haven't run `nbdev_new`, run:

     ```bash
     make nbdev-init
     ```

7. Export notebooks, run tests, and prepare release
   - Export code from notebooks:

     ```bash
     make nbdev-export
     ```

   - Run notebook-based tests:

     ```bash
     make nbdev-test
     ```

   - Clean and prepare for release:

     ```bash
     make nbdev-prepare
     ```

8. Build / publish (optional)
   - Publish to PyPI (requires credentials): `make nbdev-pypi`
   - Build & publish Conda package: `make nbdev-conda`

9. Example `settings.ini` (edit values to match your project)

```
[DEFAULT]
lib_name = mini_rlm
lib_path = mini_rlm
nbs_path = nbs
doc_path = docs
user = your-github-username
repo = your-github-username/mini-rlm
branch = main
version = 0.0.0
description = Recursive Language Model helpers
author = Your Name
author_email = you@example.com
license = MIT
min_python = 3.8
keywords = rlm,lisette,nbdev
```

10. Next actions (pick one)
    - I can populate `settings.ini` now with your values.
    - I can add `#| export` markers to selected notebook cells (tell me cell numbers).
    - I can create the venv and run the Makefile targets for you.

---
Saved to `TODO.md`.
