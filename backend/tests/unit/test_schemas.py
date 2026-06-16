from datetime import date

import pytest
from pydantic import ValidationError

from src.schemas.search import SearchRequest


def test_search_request_valid():
    req = SearchRequest(
        origin="PEK",
        destination="SHA",
        departure_date=date(2026, 8, 1),
    )
    assert req.adults == 1
    assert req.cabin_class == "ECONOMY"


def test_search_request_lowercase_iata_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(origin="pek", destination="SHA", departure_date=date(2026, 8, 1))


def test_search_request_invalid_iata_length():
    with pytest.raises(ValidationError):
        SearchRequest(origin="PEEK", destination="SHA", departure_date=date(2026, 8, 1))


def test_search_request_return_before_departure_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(
            origin="PEK",
            destination="SHA",
            departure_date=date(2026, 8, 5),
            return_date=date(2026, 8, 1),  # 早于出发日期
        )


def test_search_request_adults_out_of_range():
    with pytest.raises(ValidationError):
        SearchRequest(origin="PEK", destination="SHA", departure_date=date(2026, 8, 1), adults=0)
    with pytest.raises(ValidationError):
        SearchRequest(origin="PEK", destination="SHA", departure_date=date(2026, 8, 1), adults=10)
