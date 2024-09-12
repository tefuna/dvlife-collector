import re
from datetime import date
from decimal import Decimal

import gspread
import pandas

from dvlife_collector.domain.model.position import Position

# import pytest


# @pytest.fixture(scope="function", autouse=True)
# @pytest.fixture()
# def setup():
#     print("setup")
#     yield


def test_filter():
    a: list[str] = []
    tester = [
        ["投資候補："],
        [],
        [],
        ["含", "売", "ティッカー"],
        ["o", "", "8591"],
        ["x", "", "1605"],
        ["x", "", "1719"],
        ["x", "", "1928"],
        ["x", "", "1951"],
        ["x", "", "2154"],
        ["x", "", "3003"],
        ["x", "", "3176"],
        ["x", "", "3280"],
        ["x", "", "3431"],
        ["x", "", "4093"],
        ["x", "", "4202"],
        ["x", "", "4503"],
        ["x", "売", "4668"],
        ["x", "売", "4745"],
        ["x", "", "5105"],
        ["x", "", "5288"],
        ["x", "", "5334"],
        ["x", "", "5401"],
        ["x", "", "5406"],
        ["x", "", "5411"],
        ["x", "", "5911"],
        ["x", "", "6089"],
        ["x", "", "6223"],
        ["x", "", "6248"],
        ["x", "", "6301"],
        ["x", "", "6432"],
        ["x", "", "7148"],
        ["x", "", "7164"],
        ["x", "", "7246"],
        ["x", "", "7267"],
        ["x", "", "7272"],
        ["x", "", "7414"],
        ["x", "", "7438"],
        ["x", "", "8002"],
        ["x", "", "8014"],
        ["x", "", "8020"],
        ["x", "", "8031"],
        ["x", "", "8058"],
        ["x", "", "8058"],
        ["x", "", "8098"],
        ["x", "", "8306"],
        ["x", "", "8309"],
        ["x", "", "8316"],
        ["x", "", "8425"],
        ["x", "", "8439"],
        ["x", "", "8473"],
        ["x", "", "8566"],
        ["x", "", "8584"],
        ["x", "", "8593"],
        ["x", "", "8593"],
        ["x", "", "8596"],
        ["x", "", "8630"],
        ["x", "", "8725"],
        ["x", "", "8750"],
    ]
    for i in tester:
        if len(i) >= 3 and i[0] == "o":
            a.append(i[2])
    print(a)


def test_gspread():
    GS_TARGET = {
        "url": "https://docs.google.com/spreadsheets/d/1v5RfVBFyBDAEvpTr1Po7NcVMKuaJ0nQRemxYVnRjpPE/edit?gid=563532298#gid=563532298",
        "sheetname": "投資候補",
    }
    GS_CELL = {
        "ROW_START": 6,
        "COL_TICKER": 3,
        "COL_WRITER": 6,
    }

    gc = gspread.oauth(credentials_filename="/workspaces/gspread_client_secret.json")

    sheet = gc.open_by_url(GS_TARGET["url"]).worksheet(GS_TARGET["sheetname"])
    ticker_cols: list[str] = sheet.col_values(GS_CELL["COL_TICKER"])

    print(ticker_cols)

    tickers = [s for s in ticker_cols if re.match("[0-9A-Z]{4}", s)]
    print(tickers)


# Update a range of cells using the top left corner address
# wks.update([[1, 2], [3, 4]], "A1")


def test_ref():
    a = [1, 2, 3]
    b = a

    a.append(4)
    print(a)
    print(b)


def test_strip():
    a = "24万"

    # a = a.replace()

    # if a.find("万") != -1:
    #     a = a.replace("万", "000")

    print(a)


def test_list_extend():
    a = [1, 2, 3]
    b = []
    c = [4, 5, 6]

    c.extend(a)
    c.extend(b)

    print(c)


def test_isdecimal():
    a_price = "35.11"
    c_price = "--"

    a_dec = Decimal(a_price)
    print(a_dec)
    try:
        float(c_price)
    except ValueError:
        print("is not decimal")


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
    # df.to_csv("/workspaces/aaa2.csv", index=False)
    assert True
