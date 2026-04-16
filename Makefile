.PHONY: all setup validate build test open clean help

PYTHON := uv run python
VENV := .venv

help:
	@echo "Targets:"
	@echo "  setup     create .venv and install deps (uv)"
	@echo "  validate  reproduce Eurostat PPS index within +/- 1 pp"
	@echo "  build     generate web/data.json, web/index.html, web/story.html, web/story.ro.html"
	@echo "  test      run pytest"
	@echo "  open      open the plain-language story page in a browser"
	@echo "  all       setup + validate + build"
	@echo "  clean     remove .venv and generated web artifacts"

$(VENV):
	uv venv
	uv pip install -e ".[dev]"

setup: $(VENV)

validate: $(VENV)
	$(PYTHON) -m real_statistic validate

build: $(VENV)
	$(PYTHON) -m real_statistic build

test: $(VENV)
	uv run pytest -q

open:
	open docs/index.html

all: setup validate build
	@echo "Ready. Pages:"
	@echo "  docs/index.html        landing (Romanian story)"
	@echo "  docs/en.html           English story"
	@echo "  docs/technical.html    methodology and full data tables"

clean:
	rm -rf $(VENV) docs/index.html docs/en.html docs/technical.html docs/data.json
	rm -rf src/*.egg-info .pytest_cache __pycache__
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
