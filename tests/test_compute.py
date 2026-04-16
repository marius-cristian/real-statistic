from __future__ import annotations

from datetime import date

import pytest

from real_statistic.compute import (
    basket_cost_eur,
    baskets_per_month,
    cross_country_index,
    divergence,
    relative_purchasing_power,
    reproduce_official_pps,
    salary_net_eur,
)
from real_statistic.schema import (
    BasketDefinition,
    BasketItem,
    BasketsFile,
    FxRate,
    MacroFile,
    MacroYear,
    PriceRow,
    PricesFile,
    Salary,
    SalariesFile,
    Source,
)


def _src() -> Source:
    return Source(url="https://example.test/", date_retrieved=date(2026, 4, 16))


@pytest.fixture
def synthetic_macro() -> MacroFile:
    # Construct so RO ~ 78, FR ~ 100, DE ~ 115, EU27 = 100.
    # Formula: idx = 100 * (gdp / pop / ppp) / (gdp_eu / pop_eu / ppp_eu)
    # Pick EU27: gdp=15e6, pop=450e6, ppp=1.0 -> pps_per_cap = 33333.33
    # RO: target 78 -> pps_per_cap = 26000 -> gdp/pop = 26000 * ppp
    #   ppp=0.5 -> gdp/pop = 13000; pop=19e6 -> gdp_millions = 247000
    # FR: target 100 -> pps_per_cap = 33333.33; ppp=1.1; pop=68e6 -> gdp/pop=36666.66 -> 2493333 millions
    # DE: target 115 -> pps_per_cap = 38333.33; ppp=1.0; pop=84e6 -> gdp/pop=38333.33 -> 3220000 millions
    return MacroFile(
        countries={
            "RO": MacroYear(
                year=2024, gdp_nominal_eur_millions=247000, population=19_000_000,
                ppp=0.5, price_level_index=55, official_gdp_pps_index=78.0,
                source=_src(),
            ),
            "FR": MacroYear(
                year=2024, gdp_nominal_eur_millions=2_493_333, population=68_000_000,
                ppp=1.1, price_level_index=108, official_gdp_pps_index=100.0,
                source=_src(),
            ),
            "DE": MacroYear(
                year=2024, gdp_nominal_eur_millions=3_220_000, population=84_000_000,
                ppp=1.0, price_level_index=110, official_gdp_pps_index=115.0,
                source=_src(),
            ),
            "EU27": MacroYear(
                year=2024, gdp_nominal_eur_millions=15_000_000, population=450_000_000,
                ppp=1.0, price_level_index=100, official_gdp_pps_index=100.0,
                source=_src(),
            ),
        },
        fx_rates=[
            FxRate(pair="EUR_RON", rate=5.0, date=date(2026, 4, 15), source=_src()),
            FxRate(pair="EUR_EUR", rate=1.0, date=date(2026, 4, 15), source=_src()),
        ],
    )


def test_reproduce_pps_matches_target(synthetic_macro):
    reproduced = reproduce_official_pps(synthetic_macro)
    assert reproduced["EU27"] == pytest.approx(100.0, abs=0.01)
    assert reproduced["RO"] == pytest.approx(78.0, abs=0.5)
    assert reproduced["FR"] == pytest.approx(100.0, abs=0.5)
    assert reproduced["DE"] == pytest.approx(115.0, abs=0.5)


def test_salary_net_eur_converts_ron(synthetic_macro):
    salaries = SalariesFile(
        salaries=[
            Salary(country="RO", year=2024, median_net_monthly=5000, currency="RON", source=_src()),
            Salary(country="FR", year=2024, median_net_monthly=2200, currency="EUR", source=_src()),
            Salary(country="DE", year=2024, median_net_monthly=2800, currency="EUR", source=_src()),
        ]
    )
    eur = salary_net_eur(salaries, synthetic_macro)
    assert eur["RO"] == pytest.approx(1000.0)  # 5000 / 5
    assert eur["FR"] == pytest.approx(2200.0)
    assert eur["DE"] == pytest.approx(2800.0)


def _make_baskets() -> BasketsFile:
    return BasketsFile(
        items={
            "rent": BasketItem(id="rent", description="rent", unit="mo", amortization_months=1),
            "phone": BasketItem(id="phone", description="phone", unit="unit", amortization_months=24),
        },
        baskets=[
            BasketDefinition(name="survival", description="x", items={"rent": 1.0}),
            BasketDefinition(name="middle_class", description="x", items={"rent": 1.0, "phone": 1.0}),
            BasketDefinition(name="global", description="x", items={"phone": 1.0}),
            BasketDefinition(name="housing_only", description="x", items={"rent": 1.0}),
        ],
    )


def _make_prices() -> dict[str, PricesFile]:
    return {
        "RO": PricesFile(country="RO", prices=[
            PriceRow(item_id="rent", price=1500.0, currency="RON", unit="mo", source=_src()),
            PriceRow(item_id="phone", price=4800.0, currency="RON", unit="unit", source=_src()),
        ]),
        "FR": PricesFile(country="FR", prices=[
            PriceRow(item_id="rent", price=900.0, currency="EUR", unit="mo", source=_src()),
            PriceRow(item_id="phone", price=1000.0, currency="EUR", unit="unit", source=_src()),
        ]),
        "DE": PricesFile(country="DE", prices=[
            PriceRow(item_id="rent", price=800.0, currency="EUR", unit="mo", source=_src()),
            PriceRow(item_id="phone", price=1000.0, currency="EUR", unit="unit", source=_src()),
        ]),
    }


def test_basket_cost_eur_amortizes_and_converts(synthetic_macro):
    baskets = _make_baskets()
    prices = _make_prices()
    eur, breakdown = basket_cost_eur(baskets, prices, synthetic_macro)
    # middle_class in DE = 800 (rent) + 1000/24 (phone amortized) = 841.666 EUR
    assert eur[("middle_class", "DE")] == pytest.approx(800 + 1000 / 24)
    # global in RO = 4800/24 = 200 RON -> 40 EUR at 5 RON/EUR
    assert eur[("global", "RO")] == pytest.approx(40.0)
    # RO survival: 1500 RON rent -> 300 EUR
    assert eur[("survival", "RO")] == pytest.approx(300.0)
    # breakdown sums to total
    assert sum(breakdown[("middle_class", "DE")].values()) == pytest.approx(eur[("middle_class", "DE")])


def test_baskets_per_month_cube(synthetic_macro):
    baskets = _make_baskets()
    prices = _make_prices()
    eur_cost, _ = basket_cost_eur(baskets, prices, synthetic_macro)
    salary_eur = {"RO": 1000.0, "FR": 2200.0, "DE": 2800.0}
    bpm = baskets_per_month(eur_cost, salary_eur, [b.name for b in baskets.baskets])
    # RO salary (1000 EUR) on RO survival (300 EUR) = 3.333 baskets/month
    assert bpm[("survival", "RO", "RO")] == pytest.approx(1000.0 / 300.0)
    # RO salary on FR survival (900 EUR) = 1.111
    assert bpm[("survival", "RO", "FR")] == pytest.approx(1000.0 / 900.0)
    # DE salary on RO survival = 2800/300 = 9.333 (a "DE tourist in RO" case)
    assert bpm[("survival", "DE", "RO")] == pytest.approx(2800.0 / 300.0)


def test_relative_purchasing_power_anchor(synthetic_macro):
    baskets = _make_baskets()
    prices = _make_prices()
    eur, _ = basket_cost_eur(baskets, prices, synthetic_macro)
    salary_eur = {"RO": 1000.0, "FR": 2200.0, "DE": 2800.0}
    bpm = baskets_per_month(eur, salary_eur, [b.name for b in baskets.baskets])
    rpp = relative_purchasing_power(bpm)
    assert rpp[("middle_class", "DE", "DE")] == pytest.approx(100.0)


def test_cross_index_local_is_100(synthetic_macro):
    baskets = _make_baskets()
    prices = _make_prices()
    eur, _ = basket_cost_eur(baskets, prices, synthetic_macro)
    salary_eur = {"RO": 1000.0, "FR": 2200.0, "DE": 2800.0}
    bpm = baskets_per_month(eur, salary_eur, [b.name for b in baskets.baskets])
    cross = cross_country_index(bpm)
    for c in ("RO", "FR", "DE"):
        for b in ("survival", "middle_class", "global", "housing_only"):
            assert cross[(b, c, c)] == pytest.approx(100.0)


def test_divergence_sign(synthetic_macro):
    baskets = _make_baskets()
    prices = _make_prices()
    eur, _ = basket_cost_eur(baskets, prices, synthetic_macro)
    salary_eur = {"RO": 1000.0, "FR": 2200.0, "DE": 2800.0}
    bpm = baskets_per_month(eur, salary_eur, [b.name for b in baskets.baskets])
    reproduced = reproduce_official_pps(synthetic_macro)
    diverg = divergence(bpm, reproduced, [b.name for b in baskets.baskets])
    assert diverg[("middle_class", "DE")] == pytest.approx(0.0, abs=1e-6)


def test_missing_item_price_raises(synthetic_macro):
    baskets = _make_baskets()
    prices = {
        "RO": PricesFile(country="RO", prices=[
            PriceRow(item_id="rent", price=1500.0, currency="RON", unit="mo", source=_src()),
        ]),  # missing "phone"
        "FR": _make_prices()["FR"],
        "DE": _make_prices()["DE"],
    }
    with pytest.raises(ValueError, match="Missing price for item_id=phone"):
        basket_cost_eur(baskets, prices, synthetic_macro)
