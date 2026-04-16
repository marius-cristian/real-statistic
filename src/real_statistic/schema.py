from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


CountryCode = Literal["RO", "FR", "DE", "EU27"]
Currency = Literal["RON", "EUR"]
BasketName = Literal["survival", "middle_class", "global", "housing_only"]


class Source(BaseModel):
    url: HttpUrl
    date_retrieved: date
    notes: str | None = None


class MacroYear(BaseModel):
    year: int
    gdp_nominal_eur_millions: float
    population: int
    ppp: float = Field(description="Local currency units per 1 EUR of real purchasing power")
    price_level_index: float = Field(description="EU27 = 100")
    official_gdp_pps_index: float = Field(description="EU27 = 100, as published by Eurostat")
    source: Source


class FxRate(BaseModel):
    pair: str = Field(description="e.g. EUR_RON")
    rate: float = Field(description="Units of quote currency per 1 unit of base")
    date: date
    source: Source


class MacroFile(BaseModel):
    countries: dict[CountryCode, MacroYear]
    fx_rates: list[FxRate]


class Salary(BaseModel):
    country: CountryCode
    year: int
    median_net_monthly: float
    mean_net_monthly: float | None = None
    currency: Currency
    source: Source


class SalariesFile(BaseModel):
    salaries: list[Salary]


class BasketItem(BaseModel):
    id: str
    description: str
    unit: str
    amortization_months: int = Field(
        default=1,
        description="Divides a durable's full price across N months; 1 = recurring monthly cost",
    )


class BasketDefinition(BaseModel):
    name: BasketName
    description: str
    items: dict[str, float] = Field(description="item_id -> monthly quantity")


class BasketsFile(BaseModel):
    items: dict[str, BasketItem] = Field(description="Canonical item catalog")
    baskets: list[BasketDefinition]


class PriceRow(BaseModel):
    item_id: str
    price: float
    currency: Currency
    unit: str
    source: Source

    @field_validator("price")
    @classmethod
    def positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be positive")
        return v


class PricesFile(BaseModel):
    country: CountryCode
    prices: list[PriceRow]
