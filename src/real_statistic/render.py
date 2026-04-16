"""Render compute results into a single static HTML file via Jinja2."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .compute import ComputedResults
from .schema import BasketsFile, MacroFile, PricesFile, SalariesFile


def _tuple_map_to_nested(m: dict) -> dict:
    """Convert {(a,b): v} or {(a,b,c): v} dict to nested JSON-friendly dict."""
    out: dict = {}
    for key, value in m.items():
        if isinstance(key, tuple):
            cursor = out
            for segment in key[:-1]:
                cursor = cursor.setdefault(segment, {})
            cursor[key[-1]] = value
        else:
            out[key] = value
    return out


def results_to_json(
    results: ComputedResults,
    macro: MacroFile,
    salaries: SalariesFile,
    baskets: BasketsFile,
    prices_by_country: dict[str, PricesFile],
) -> dict:
    basket_names = [b.name for b in baskets.baskets]
    countries = list(macro.countries.keys())

    return {
        "meta": {
            "countries": countries,
            "basket_names": basket_names,
        },
        "macro": {
            code: {
                "year": row.year,
                "gdp_nominal_eur_millions": row.gdp_nominal_eur_millions,
                "population": row.population,
                "ppp": row.ppp,
                "price_level_index": row.price_level_index,
                "official_gdp_pps_index": row.official_gdp_pps_index,
                "source_url": str(row.source.url),
            }
            for code, row in macro.countries.items()
        },
        "fx_rates": [
            {
                "pair": fx.pair,
                "rate": fx.rate,
                "date": fx.date.isoformat(),
                "source_url": str(fx.source.url),
            }
            for fx in macro.fx_rates
        ],
        "salaries": [
            {
                "country": row.country,
                "year": row.year,
                "median_net_monthly": row.median_net_monthly,
                "mean_net_monthly": row.mean_net_monthly,
                "currency": row.currency,
                "source_url": str(row.source.url),
            }
            for row in salaries.salaries
        ],
        "baskets": [
            {
                "name": b.name,
                "description": b.description,
                "items": dict(b.items),
            }
            for b in baskets.baskets
        ],
        "items": {
            item_id: item.description for item_id, item in baskets.items.items()
        },
        "prices": {
            country: [
                {
                    "item_id": r.item_id,
                    "price": r.price,
                    "currency": r.currency,
                    "unit": r.unit,
                    "source_url": str(r.source.url),
                    "notes": r.source.notes,
                }
                for r in pf.prices
            ]
            for country, pf in prices_by_country.items()
        },
        "reproduced_pps_index": results.reproduced_pps_index,
        "salary_net_eur": results.salary_net_eur,
        "basket_cost_eur": _tuple_map_to_nested(results.basket_cost_eur),
        "basket_item_breakdown": _tuple_map_to_nested(results.basket_item_breakdown),
        "baskets_per_month": _tuple_map_to_nested(results.baskets_per_month),
        "rpp": _tuple_map_to_nested(results.rpp),
        "divergence": _tuple_map_to_nested(results.divergence),
        "cross_index": _tuple_map_to_nested(results.cross_index),
    }


def render_html(payload: dict, template_dir: Path, output_path: Path) -> None:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("template.html.j2")
    html = template.render(data_json=json.dumps(payload, indent=2, default=str))
    output_path.write_text(html, encoding="utf-8")


def render_story_html(payload: dict, template_dir: Path, output_path: Path) -> None:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("story.html.j2")
    html = template.render(data_json=json.dumps(payload, indent=2, default=str))
    output_path.write_text(html, encoding="utf-8")


def render_story_ro_html(payload: dict, template_dir: Path, output_path: Path) -> None:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("story.ro.html.j2")
    html = template.render(data_json=json.dumps(payload, indent=2, default=str))
    output_path.write_text(html, encoding="utf-8")
