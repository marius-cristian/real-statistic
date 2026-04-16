from __future__ import annotations

from datetime import date

from real_statistic.schema import FxRate, MacroFile, MacroYear, Source
from real_statistic.validate import validate_pps


def _src():
    return Source(url="https://example.test/", date_retrieved=date(2026, 4, 16))


def test_validation_passes_within_tolerance():
    macro = MacroFile(
        countries={
            "EU27": MacroYear(year=2024, gdp_nominal_eur_millions=15_000_000, population=450_000_000,
                              ppp=1.0, price_level_index=100, official_gdp_pps_index=100.0, source=_src()),
            "DE":   MacroYear(year=2024, gdp_nominal_eur_millions=3_220_000, population=84_000_000,
                              ppp=1.0, price_level_index=110, official_gdp_pps_index=115.0, source=_src()),
        },
        fx_rates=[FxRate(pair="EUR_EUR", rate=1.0, date=date(2026, 4, 15), source=_src())],
    )
    results = validate_pps(macro)
    de_row = next(r for r in results if r.country == "DE")
    assert de_row.passes
    assert abs(de_row.delta_pp) < 1.0


def test_validation_fails_when_official_wrong():
    macro = MacroFile(
        countries={
            "EU27": MacroYear(year=2024, gdp_nominal_eur_millions=15_000_000, population=450_000_000,
                              ppp=1.0, price_level_index=100, official_gdp_pps_index=100.0, source=_src()),
            "RO":   MacroYear(year=2024, gdp_nominal_eur_millions=247_000, population=19_000_000,
                              ppp=0.5, price_level_index=55,
                              official_gdp_pps_index=200.0,  # deliberately wrong
                              source=_src()),
        },
        fx_rates=[FxRate(pair="EUR_RON", rate=5.0, date=date(2026, 4, 15), source=_src())],
    )
    results = validate_pps(macro)
    ro_row = next(r for r in results if r.country == "RO")
    assert not ro_row.passes
