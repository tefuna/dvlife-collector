from datetime import date
from decimal import Decimal

import pytest

from dvlife_collector.domain.model.position import Position
from dvlife_collector.domain.model.ticker import Ticker


# @pytest.fixture(scope="function", autouse=True)
@pytest.fixture()
def setup():
    print("setup")
    yield


def test_main():
    assert True


def test_main2():
    position = Position(Ticker("1111"), date.today(), 1, Decimal(101), Decimal(201))
    assert position.quantity == 1
