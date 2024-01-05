import time
from decimal import Decimal
from logging import getLogger

from bs4 import BeautifulSoup
from constant.bank import Bank
from domain.model.position_by_bank import PositionByBank
from domain.model.ticker import Ticker
from infrastructure.position.page.page_base import PageBase
from selenium.webdriver.common.by import By

log = getLogger(__name__)

URL = {
    "login": "https://trade.sbineomobile.co.jp/login",
    "portfolio": "https://trade.sbineomobile.co.jp/account/portfolio",
}


class NeomobiPage(PageBase):
    def _move_to_target_page(self) -> None:
        # ログイン
        self.driver.get(URL["login"])
        self.driver.find_element(By.NAME, "username").send_keys(self._credential.username)
        self.driver.find_element(By.NAME, "password").send_keys(self._credential.password)
        self.driver.find_element(By.ID, "neo-login-btn").click()

        # ポートフォリオページへ遷移
        self.driver.get(URL["portfolio"])
        time.sleep(3)

        html01 = self.driver.page_source
        while True:
            self.driver.execute_script(
                "arguments[0].scrollTop =arguments[1];", self.driver.find_element(By.CLASS_NAME, "sp-main"), 1000000
            )
            time.sleep(1)

            # 前回スクロールとhtmlの変更がない = スクロール終了
            html02 = self.driver.page_source
            if html01 != html02:
                html01 = html02
            else:
                break

        # html parse
        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        self.__target_tags = soup.select("section.panels")

    def _parse(self) -> list[PositionByBank]:
        positions = []
        for section in self.__target_tags:
            ticker = section.select_one("p").get_text().strip()
            c_price = section.select_one("tr:nth-child(1) td span").get_text().replace(",", "").strip()
            quantity = section.select_one("tr:nth-child(2) td span").get_text().replace(",", "").strip()
            a_price = section.select_one("tr:nth-child(5) span").get_text().replace(",", "").strip()
            try:
                c_price_dec = Decimal(c_price)
            except Exception:
                log.warn("Cannot parse ticker: %s", ticker)
                continue
            position = PositionByBank(Ticker(ticker), Bank.NEOMOBI, int(quantity), Decimal(a_price), c_price_dec)
            positions.append(position)

        return positions
