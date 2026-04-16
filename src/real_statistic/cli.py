from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .compute import run as compute_run
from .load import load_baskets, load_macro, load_prices, load_salaries
from .render import render_html, render_story_html, render_story_ro_html, results_to_json
from .validate import format_validation, validate_pps

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
WEB_DIR = REPO_ROOT / "docs"


def cmd_validate(_args: argparse.Namespace) -> int:
    macro = load_macro(DATA_DIR)
    results = validate_pps(macro)
    print(format_validation(results))
    return 0 if all(r.passes for r in results) else 1


def cmd_build(_args: argparse.Namespace) -> int:
    macro = load_macro(DATA_DIR)
    salaries = load_salaries(DATA_DIR)
    baskets = load_baskets(DATA_DIR)
    prices = load_prices(DATA_DIR)

    missing = [c for c in ("RO", "FR", "DE") if c not in prices]
    if missing:
        print(f"ERROR: missing price files for {missing}", file=sys.stderr)
        return 2

    validation = validate_pps(macro)
    print(format_validation(validation))
    if not all(r.passes for r in validation):
        print("PPS reproduction failed. Aborting build.", file=sys.stderr)
        return 1

    results = compute_run(macro, salaries, baskets, prices)
    payload = results_to_json(results, macro, salaries, baskets, prices)

    data_json_path = WEB_DIR / "data.json"
    data_json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {data_json_path}")

    render_story_ro_html(payload, WEB_DIR, WEB_DIR / "index.html")
    print(f"Wrote {WEB_DIR / 'index.html'} (Romanian story, landing page)")

    render_story_html(payload, WEB_DIR, WEB_DIR / "en.html")
    print(f"Wrote {WEB_DIR / 'en.html'} (English story)")

    render_html(payload, WEB_DIR, WEB_DIR / "technical.html")
    print(f"Wrote {WEB_DIR / 'technical.html'} (full methodology and data tables)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="real-statistic")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_validate = sub.add_parser("validate", help="Reproduce Eurostat PPS from raw inputs (±1pp gate)")
    p_validate.set_defaults(func=cmd_validate)

    p_build = sub.add_parser("build", help="Validate, compute, render web/index.html")
    p_build.set_defaults(func=cmd_build)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
