import dataclasses
from datetime import date
from decimal import Decimal

import pandas

from dvlife_collector.domain.model.position import Position
from dvlife_collector.domain.model.ticker import Ticker

# import pytest


# @pytest.fixture(scope="function", autouse=True)
# @pytest.fixture()
# def setup():
#     print("setup")
#     yield


def test_pandas():
    pos1 = Position("1111", date.today(), 1, Decimal(101), Decimal(201))
    pos2 = Position("1112", date.today(), 1, Decimal(102), Decimal(202))

    lis = [pos2, pos1]
    s_lis = sorted(lis, key=lambda a: a.ticker)

    # d_lis = list(map(lambda x: dataclasses.asdict(x), s_lis))

    # print(d_lis)
    pandas.options.display.precision = 2
    df = pandas.DataFrame(s_lis)
    print(df)
    print(df.columns)
    # df['ticker'] = df['ticker'].ticker
    # df["ticker"] = df["ticker"].map(lambda x: x.ticker)
    # df["base_date"] = df["base_date"].map(lambda x: x.)
    df.round(
        {
            "acquisition_price": 2,
            "current_price": 2,
            "book_value": 2,
            "market_value": 2,
            "valuation_value": 2,
            "valuation_ratio": -2,
        }
    )
    df.to_csv("/workspaces/aaa2.csv", index=False)
    assert True
