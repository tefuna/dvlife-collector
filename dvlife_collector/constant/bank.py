from enum import Enum


class Bank(Enum):
    RAKUTEN = {"code": "0661", "cls": "RakutenPage"}
    SBI = {"code": "0988", "cls": "SBIPage"}
    NEOMOBI = {"code": "9999", "cls": "NeomobiPage"}
