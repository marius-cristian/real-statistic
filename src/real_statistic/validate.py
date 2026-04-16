"""Validation: reproduced PPS index must match Eurostat's published figure within ±1pp."""

from __future__ import annotations

from dataclasses import dataclass

from .compute import reproduce_official_pps
from .schema import MacroFile

TOLERANCE_PP = 1.0


@dataclass
class ValidationResult:
    country: str
    official: float
    reproduced: float
    delta_pp: float
    passes: bool


def validate_pps(macro: MacroFile) -> list[ValidationResult]:
    reproduced = reproduce_official_pps(macro)
    results: list[ValidationResult] = []
    for code, row in macro.countries.items():
        delta = reproduced[code] - row.official_gdp_pps_index
        results.append(
            ValidationResult(
                country=code,
                official=row.official_gdp_pps_index,
                reproduced=reproduced[code],
                delta_pp=delta,
                passes=abs(delta) <= TOLERANCE_PP,
            )
        )
    return results


def format_validation(results: list[ValidationResult]) -> str:
    lines = ["country  official  reproduced  delta_pp  pass"]
    for r in results:
        lines.append(
            f"{r.country:<7}  {r.official:>8.2f}  {r.reproduced:>10.2f}  "
            f"{r.delta_pp:>+7.2f}   {'OK' if r.passes else 'FAIL'}"
        )
    return "\n".join(lines)
