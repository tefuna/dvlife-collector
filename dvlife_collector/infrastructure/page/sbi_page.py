import time
from decimal import Decimal
from logging import getLogger

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from constant.bank import Bank
from domain.model.position_by_bank import PositionByBank
from domain.model.ticker import Ticker
from infrastructure.page.page_base import PageBase
from selenium.webdriver.common.by import By

log = getLogger(__name__)

URL = {
    "login": "https://www.sbisec.co.jp/ETGate",
}
ACC_TYPE_TK = "TOKUTEI"
ACC_TYPE_IP = "IPPAN"


class SbiPage(PageBase):
    def _move_to_target_page(self) -> None:
        # ログイン
        self.driver.get(URL["login"])

        self.driver.find_element(By.NAME, "user_id").send_keys(self._credential.username)
        self.driver.find_element(By.NAME, "user_password").send_keys(self._credential.password)
        self.driver.find_element(By.NAME, "ACT_login").click()

        # 口座（円建）
        self.__target_tags_ja = self.__move_to_ja_account()

        # 口座（外貨建）
        self.__target_tags_us = self.__move_to_us_account()

    def __move_to_ja_account(self) -> dict[str, ResultSet]:
        self.driver.find_element(By.XPATH, '//*[@id="link02M"]/ul/li[3]/a').click()
        time.sleep(1)

        # html parse
        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        trs = {}
        result_set = soup.select(
            "body > div:nth-child(1) > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(2) > td > table:nth-child(1) > tbody > tr > td > form > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > table:nth-child(19) > tbody > tr > td:nth-child(3) > table:nth-child(4) > tbody > tr"  # noqa: E501
        )
        trs[ACC_TYPE_TK] = result_set[2:]
        return trs

    def __move_to_us_account(self) -> dict[str, ResultSet]:
        self.driver.find_element(By.XPATH, '//*[@id="navi02P"]/ul/li[2]/div/a').click()
        time.sleep(1)

        # html parse
        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        trs = {}
        result_set = soup.select(
            "body > div:nth-child(1) > table:nth-child(14) > tbody > tr > td:nth-child(1) > table > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > table:nth-child(7) > tbody > tr > td:nth-child(3) > table:nth-child(7) > tbody > tr"  # noqa: E501
        )
        trs[ACC_TYPE_TK] = result_set[1:]
        result_set = soup.select(
            "body > div:nth-child(1) > table:nth-child(14) > tbody > tr > td:nth-child(1) > table > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > table:nth-child(7) > tbody > tr > td:nth-child(3) > table:nth-child(10) > tbody > tr"  # noqa: E501
        )
        trs[ACC_TYPE_IP] = result_set[1:]
        return trs

    def _parse(self) -> list[PositionByBank]:
        positions = []
        positions.extend(self.__get_positions_jp())
        positions.extend(self.__get_positions_us())
        return positions

    def __get_positions_jp(self) -> list[PositionByBank]:
        positions = []

        # 特定口座
        trs = self.__target_tags_ja[ACC_TYPE_TK]
        index = 0
        while index < len(trs):
            tds1 = trs[index].select("td")
            tds2 = trs[index + 1].select("td")

            ticker = list(tds1[0].stripped_strings)[0]
            quantity = tds2[0].get_text().replace(",", "").strip()
            a_price = tds2[1].get_text().replace(",", "").strip()
            c_price = tds2[2].get_text().replace(",", "").strip()
            position = PositionByBank(Ticker(ticker), Bank.SBI, int(quantity), Decimal(a_price), Decimal(c_price))
            positions.append(position)

            index += 2

        return positions

    def __get_positions_us(self) -> list[PositionByBank]:
        positions = []

        # 特定口座分
        trs = self.__target_tags_us[ACC_TYPE_TK]
        index = 0
        while index < len(trs):
            tds1 = trs[index].select("td")
            tds2 = trs[index + 1].select("td")

            ticker = list(tds1[0].stripped_strings)[0]
            quantity = tds2[0].get_text().replace(",", "").strip()
            a_price = tds2[1].get_text().replace(",", "").strip()
            c_price = tds2[2].get_text().replace(",", "").strip()
            position = PositionByBank(Ticker(ticker), Bank.SBI, int(quantity), Decimal(a_price), Decimal(c_price))
            positions.append(position)

            index += 2

        # 一般口座
        trs = self.__target_tags_us[ACC_TYPE_IP]
        index = 0
        while index < len(trs):
            tds1 = trs[index].select("td")
            tds2 = trs[index + 1].select("td")

            ticker = list(tds1[0].stripped_strings)[0]
            quantity = tds2[0].get_text().replace(",", "").strip()
            a_price = tds2[1].get_text().replace(",", "").strip()
            c_price = tds2[2].get_text().replace(",", "").strip()
            # 設定がない場合は、current_priceと合わせる
            if not str(a_price).isdecimal():
                a_price = c_price
            position = PositionByBank(Ticker(ticker), Bank.SBI, int(quantity), Decimal(a_price), Decimal(c_price))
            positions.append(position)

            index += 2

        return positions
