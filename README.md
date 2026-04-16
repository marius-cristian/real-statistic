# real-statistic

Challenges the Eurostat "Romania at 78% of EU average" narrative by pricing real baskets at real retailers and dividing by real median salaries, for Romania, France, and Germany.

Built with `uv`, Python 3.11+, and plain HTML + Chart.js. No build step for the web page.

## Run it yourself

Requires [uv](https://docs.astral.sh/uv/) and a browser.

```sh
make setup     # one-time: create .venv, install deps
make validate  # reproduce Eurostat's PPS index from raw inputs (+/- 1 pp gate)
make build     # regenerate docs/index.html (RO), docs/en.html, docs/technical.html, docs/data.json
make open      # open the plain-language story page in a browser
make test      # run pytest
make all       # setup + validate + build
make clean     # remove .venv and generated docs artifacts
```

No Makefile targets? `uv venv && uv pip install -e ".[dev]" && uv run python -m real_statistic build` does the same thing.

## What the three pages show

- `docs/index.html` (Romanian story, landing page) and `docs/en.html` (English story): plain-language walkthrough of the hypothesis, methodology, charts, and conclusions.
- `docs/technical.html`: technical page with full per-basket cross-country cube, PPS divergence chart, formulas, item-level price tables.
- `docs/data.json`: the raw output of the pipeline, inlined into all three HTML pages.

## Project layout

```
real-statistic/
  data/
    baskets.yaml                # canonical item list and four basket compositions
    macro.yaml                  # Eurostat GDP, population, PPP, PLI, ECB FX rates
    salaries.yaml               # median + mean net monthly salaries per country
    prices/{ro,fr,de}.yaml      # every basket item priced at a real retailer, URL + date
  src/real_statistic/
    schema.py                   # pydantic models
    load.py                     # YAML loading and validation
    compute.py                  # all formulas (see METHODOLOGY.md)
    validate.py                 # reproduces Eurostat PPS index, +/- 1 pp gate
    render.py                   # Jinja2 templating
    cli.py                      # `python -m real_statistic build | validate`
  tests/                        # unit tests for compute, validate, schema
  docs/                         # served by GitHub Pages
    template.html.j2            # technical page template
    story.html.j2               # English story page template
    story.ro.html.j2            # Romanian story page template
  METHODOLOGY.md                # theory and formulas
  SOURCES.md                    # master bibliography
```

## Adding a new data point

1. Edit the relevant YAML under `data/`. Every row needs `url` and `date_retrieved`.
2. `make build`. The pipeline validates the YAML, reproduces the PPS index as a sanity check, and regenerates the HTML.
3. If `make validate` fails with a reproduction delta over 1 pp, fix the macro inputs before proceeding.

## Not covered

- Only Romania, France, Germany. Adding countries means sourcing prices, salaries, and macro inputs for each. The schema and compute layer are country-agnostic.
- Capital-city rent only. A future iteration could add national-median rent alongside.
- Median net salary is from published statistical-office figures; some rows currently use mean where a direct median retrieval was blocked. Rows are flagged in `salaries.yaml`.

See `METHODOLOGY.md` for formulas, limitations, and the full set of caveats.
