from __future__ import annotations

from datetime import date

import pytest

from real_statistic.schema import PriceRow, Source


def test_price_must_be_positive():
    with pytest.raises(Exception):
        PriceRow(
            item_id="x",
            price=0.0,
            currency="EUR",
            unit="unit",
            source=Source(url="https://example.test/", date_retrieved=date(2026, 4, 16)),
        )
