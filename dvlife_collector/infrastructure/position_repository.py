import os

import pandas
from domain.model.position import Position
from domain.model.position_by_bank import PositionByBank
from dotenv import load_dotenv
from infrastructure.page.credential import Credential
from infrastructure.page.neomobi_page import NeomobiPage
from infrastructure.page.rakuten_page import RakutenPage
from infrastructure.page.sbi_page import SbiPage

load_dotenv()


class PositionRepository:
    def __init__(self):
        pass

    def retrieve_all_by_bank(self) -> list[PositionByBank]:
        positions_by_bank = []
        positions_by_bank.extend(self.__retrieve_rakuten())
        positions_by_bank.extend(self.__retrieve_sbi())
        positions_by_bank.extend(self.__retrieve_neomobi())
        return positions_by_bank

    def __retrieve_rakuten(self) -> list[PositionByBank]:
        username = os.environ["RAK_USER"]
        password = os.environ["RAK_PASS"]
        cred = Credential(username, password)
        return RakutenPage(cred).scrape()

    def __retrieve_sbi(self) -> list[PositionByBank]:
        username = os.environ["SBI_USER"]
        password = os.environ["SBI_PASS"]
        cred = Credential(username, password)
        return SbiPage(cred).scrape()

    def __retrieve_neomobi(self) -> list[PositionByBank]:
        username = os.environ["NEO_USER"]
        password = os.environ["NEO_PASS"]
        cred = Credential(username, password)
        return NeomobiPage(cred).scrape()

    def save(self, positions: list[Position]) -> None:
        # TODO 事前にディレクトリ作る
        sorted_pos = sorted(positions, key=lambda position: position.ticker)
        df = pandas.DataFrame(sorted_pos)
        df.to_csv(os.environ["POSITION_OUT_PATH"], sep="\t", index=False, header=False)
