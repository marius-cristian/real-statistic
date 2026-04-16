from __future__ import annotations

from pathlib import Path

import yaml

from .schema import BasketsFile, MacroFile, PricesFile, SalariesFile


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_macro(data_dir: Path) -> MacroFile:
    return MacroFile.model_validate(_read_yaml(data_dir / "macro.yaml"))


def load_salaries(data_dir: Path) -> SalariesFile:
    return SalariesFile.model_validate(_read_yaml(data_dir / "salaries.yaml"))


def load_baskets(data_dir: Path) -> BasketsFile:
    return BasketsFile.model_validate(_read_yaml(data_dir / "baskets.yaml"))


def load_prices(data_dir: Path) -> dict[str, PricesFile]:
    prices_dir = data_dir / "prices"
    out: dict[str, PricesFile] = {}
    for path in sorted(prices_dir.glob("*.yaml")):
        parsed = PricesFile.model_validate(_read_yaml(path))
        out[parsed.country] = parsed
    return out
