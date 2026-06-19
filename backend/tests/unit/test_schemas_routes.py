"""RouteCreate schema 校验。"""

import pytest
from pydantic import ValidationError

from src.schemas.routes import RouteCreate


def test_route_create_valid():
    r = RouteCreate(origin="PEK", destination="SHA")
    assert r.origin == "PEK"
    assert r.destination == "SHA"


def test_route_create_lowercase_rejected():
    with pytest.raises(ValidationError):
        RouteCreate(origin="pek", destination="SHA")


def test_route_create_too_short():
    with pytest.raises(ValidationError):
        RouteCreate(origin="PE", destination="SHA")


def test_route_create_too_long():
    with pytest.raises(ValidationError):
        RouteCreate(origin="PEEK", destination="SHA")


def test_route_create_non_alpha():
    with pytest.raises(ValidationError):
        RouteCreate(origin="P3K", destination="SHA")
