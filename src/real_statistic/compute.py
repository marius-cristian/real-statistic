"""Pure functions implementing the formulas from METHODOLOGY.md.

Section numbers in docstrings refer to METHODOLOGY.md sections.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .schema import (
    BasketDefinition,
    BasketsFile,
    MacroFile,
    PricesFile,
    SalariesFile,
)

COUNTRIES = ("RO", "FR", "DE")
DE_ANCHOR_BASKET = "middle_class"  # section 5 anchor


@dataclass(frozen=True)
class ComputedResults:
    reproduced_pps_index: dict[str, float]          # official PPS reproduction (section 1)
    salary_net_eur: dict[str, float]                # net salary in EUR (section 3)
    basket_cost_eur: dict[tuple[str, str], float]   # (basket, pricing_country) -> EUR
    basket_item_breakdown: dict[tuple[str, str], dict[str, float]]  # (basket, pc) -> item_id -> EUR/month
    baskets_per_month: dict[tuple[str, str, str], float]   # (basket, salary_c, pricing_c) -> count
    rpp: dict[tuple[str, str, str], float]           # relative PP, DE/DE/middle_class=100
    divergence: dict[tuple[str, str], float]         # official PPS - RPP[basket, c, c]
    cross_index: dict[tuple[str, str, str], float]   # 100 * bpm[b,sc,pc] / bpm[b,pc,pc]


def _fx_to_eur(macro: MacroFile, currency: str, asof=None) -> float:
    """Rate that converts one unit of `currency` into EUR.

    EUR -> 1.0. RON -> 1 / (RON per 1 EUR).
    """
    if currency == "EUR":
        return 1.0
    pair = f"EUR_{currency}"
    candidates = [fx for fx in macro.fx_rates if fx.pair == pair]
    if not candidates:
        raise ValueError(f"No FX rate for {currency}, expected pair {pair}")
    candidates.sort(key=lambda fx: fx.date, reverse=True)
    ron_per_eur = candidates[0].rate
    return 1.0 / ron_per_eur


def reproduce_official_pps(macro: MacroFile) -> dict[str, float]:
    """Section 1. Reproduce Eurostat's official GDP-per-capita PPS index, EU27=100.

    GDP_PPS_per_capita[c] = GDP_nominal_EUR[c] / population[c] / PPP[c]
    index[c] = 100 * GDP_PPS_per_capita[c] / GDP_PPS_per_capita[EU27]
    """
    eu = macro.countries["EU27"]
    eu_pps_per_cap = (eu.gdp_nominal_eur_millions * 1_000_000) / eu.population / eu.ppp

    out: dict[str, float] = {}
    for code, row in macro.countries.items():
        pps_per_cap = (row.gdp_nominal_eur_millions * 1_000_000) / row.population / row.ppp
        out[code] = 100.0 * pps_per_cap / eu_pps_per_cap
    return out


def salary_net_eur(salaries: SalariesFile, macro: MacroFile) -> dict[str, float]:
    """Section 3. Net salary converted to EUR."""
    out: dict[str, float] = {}
    for row in salaries.salaries:
        out[row.country] = row.median_net_monthly * _fx_to_eur(macro, row.currency)
    return out


def _price_lookup(prices: PricesFile) -> dict[str, tuple[float, str]]:
    return {row.item_id: (row.price, row.currency) for row in prices.prices}


def basket_cost_eur(
    baskets: BasketsFile,
    prices_by_country: dict[str, PricesFile],
    macro: MacroFile,
) -> tuple[
    dict[tuple[str, str], float],
    dict[tuple[str, str], dict[str, float]],
]:
    """Sections 2 and 3. Basket cost in EUR, per-item amortized, mixed currencies per country allowed.

    Returns (totals, breakdown) where:
        totals[(basket_name, pricing_country)]    = EUR/month for the whole basket
        breakdown[(basket_name, pc)][item_id]     = EUR/month contribution of that line
    """
    totals: dict[tuple[str, str], float] = {}
    breakdown: dict[tuple[str, str], dict[str, float]] = {}
    item_catalog = baskets.items
    for basket in baskets.baskets:
        for pc, prices in prices_by_country.items():
            lookup = _price_lookup(prices)
            total_eur = 0.0
            per_item: dict[str, float] = {}
            for item_id, qty in basket.items.items():
                if item_id not in lookup:
                    raise ValueError(
                        f"Missing price for item_id={item_id} in country={pc}. "
                        f"Every basket item must be priced in every country."
                    )
                unit_price, currency = lookup[item_id]
                fx = _fx_to_eur(macro, currency)
                amort = item_catalog[item_id].amortization_months
                contribution_eur = (unit_price * fx / amort) * qty
                total_eur += contribution_eur
                per_item[item_id] = contribution_eur
            totals[(basket.name, pc)] = total_eur
            breakdown[(basket.name, pc)] = per_item
    return totals, breakdown


def baskets_per_month(
    basket_cost_eur_map: dict[tuple[str, str], float],
    salary_eur: dict[str, float],
    basket_names: Iterable[str],
) -> dict[tuple[str, str, str], float]:
    """Section 4. The 4x3x3 cube."""
    out: dict[tuple[str, str, str], float] = {}
    for basket_name in basket_names:
        for sc in COUNTRIES:
            if sc not in salary_eur:
                continue
            for pc in COUNTRIES:
                key = (basket_name, pc)
                if key not in basket_cost_eur_map:
                    continue
                cost = basket_cost_eur_map[key]
                out[(basket_name, sc, pc)] = salary_eur[sc] / cost
    return out


def relative_purchasing_power(
    bpm: dict[tuple[str, str, str], float],
) -> dict[tuple[str, str, str], float]:
    """Section 5. RPP anchored to DE/DE/middle_class = 100."""
    anchor = bpm.get((DE_ANCHOR_BASKET, "DE", "DE"))
    if not anchor:
        raise ValueError(
            "Anchor baskets_per_month[middle_class, DE, DE] missing. Cannot compute RPP."
        )
    return {k: 100.0 * v / anchor for k, v in bpm.items()}


def divergence(
    bpm: dict[tuple[str, str, str], float],
    reproduced_index: dict[str, float],
    basket_names: Iterable[str],
) -> dict[tuple[str, str], float]:
    """Section 6. Per-basket PPS divergence.

    For each basket, rebase the same-country same-pricing bpm row so that DE
    equals DE's official PPS index. Then subtract from the official index:

        rescaled[b, c] = bpm[b, c, c] / bpm[b, DE, DE] * official_index[DE]
        divergence[b, c] = official_index[c] − rescaled[b, c]

    By construction divergence[b, DE] = 0. Positive divergence = PPS flatters
    country c in that basket. Negative = PPS understates.
    """
    de_official = reproduced_index.get("DE")
    if not de_official:
        raise ValueError("Missing reproduced PPS index for DE")
    out: dict[tuple[str, str], float] = {}
    for basket_name in basket_names:
        de_anchor = bpm.get((basket_name, "DE", "DE"))
        if not de_anchor:
            continue
        for c in COUNTRIES:
            key = (basket_name, c, c)
            if key not in bpm:
                continue
            rescaled = bpm[key] / de_anchor * de_official
            out[(basket_name, c)] = reproduced_index[c] - rescaled
    return out


def cross_country_index(
    bpm: dict[tuple[str, str, str], float],
) -> dict[tuple[str, str, str], float]:
    """Section 7. How many % of country pc's own-basket a person from sc can afford."""
    out: dict[tuple[str, str, str], float] = {}
    for (basket_name, sc, pc), value in bpm.items():
        base = bpm.get((basket_name, pc, pc))
        if not base:
            continue
        out[(basket_name, sc, pc)] = 100.0 * value / base
    return out


def run(
    macro: MacroFile,
    salaries: SalariesFile,
    baskets: BasketsFile,
    prices_by_country: dict[str, PricesFile],
) -> ComputedResults:
    reproduced = reproduce_official_pps(macro)
    salary_eur = salary_net_eur(salaries, macro)
    basket_eur, breakdown = basket_cost_eur(baskets, prices_by_country, macro)
    basket_names = [b.name for b in baskets.baskets]
    bpm = baskets_per_month(basket_eur, salary_eur, basket_names)
    rpp = relative_purchasing_power(bpm)
    diverg = divergence(bpm, reproduced, basket_names)
    cross = cross_country_index(bpm)
    return ComputedResults(
        reproduced_pps_index=reproduced,
        salary_net_eur=salary_eur,
        basket_cost_eur=basket_eur,
        basket_item_breakdown=breakdown,
        baskets_per_month=bpm,
        rpp=rpp,
        divergence=diverg,
        cross_index=cross,
    )
