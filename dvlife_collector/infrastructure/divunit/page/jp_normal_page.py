import time
from datetime import date
from decimal import Decimal
from logging import getLogger

from bs4 import BeautifulSoup
from domain.model.divunit import Divunit
from domain.model.divunit_target import DivunitTarget
from infrastructure.divunit.page.page_base import PageBase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

log = getLogger(__name__)

URL = {
    "login": "https://www.rakuten-sec.co.jp/",
}
RETRY_TIMES = 3


class JpNormalPage(PageBase):
    def _retrieve(self, targets: list[DivunitTarget]) -> list[Divunit]:
        # ログイン
        self.driver.get(URL["login"])
        self.driver.find_element(By.ID, "form-login-id").send_keys(self._credential.username)
        self.driver.find_element(By.ID, "form-login-pass").send_keys(self._credential.password)
        self.driver.find_elements(By.CLASS_NAME, "s3-form-login__btn")[0].click()

        # ティッカー分
        divunits = []
        for target in targets:
            divunits.extend(self.__parse(target))

        return divunits

    def __parse(self, target: DivunitTarget) -> list[Divunit]:
        self.driver.find_element(By.ID, "search-stock-01").send_keys(target.ticker)
        self.driver.find_element(By.ID, "search-stock-01").send_keys(Keys.ENTER)

        # 配当ページのhtml取得。リトライしてNGの場合はスキップ
        for i in range(RETRY_TIMES):
            try:
                self.driver.find_element(
                    By.XPATH,
                    '//*[@id="auto_update_field_info_jp_stock_price"]/tbody/tr/td[1]/form[2]/div[2]/table[2]/tbody/tr/td[1]/table/tbody/tr/td/div/div/ul/li[2]/a',  # noqa: E501
                ).click()
                iframe = self.driver.find_element(By.ID, "J010101-004-1")
                break
            except Exception:
                self.driver.refresh()
                time.sleep(2)

        if i >= RETRY_TIMES - 1:
            log.error("cannot find element: %s", target.ticker, exc_info=True)
            return []

        src = iframe.get_attribute("src")
        self.driver.get(src)

        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

        self.driver.back()
        try:
            results = self.__get_divunit(target.ticker, soup)
        except Exception:
            log.error("error ticker: %s", target.ticker, exc_info=True)
        return results

    def __get_divunit(self, ticker: str, soup: BeautifulSoup) -> list[Divunit]:
        # 四季報データが存在しない場合
        if soup.find(id="err_msg") is not None:
            log.warn("Japan Company Handbook data not found : %s", ticker)
            return []

        trs = soup.select("#id2 > div:nth-child(2) > div:nth-child(2) > table.tbl-data-02 > tbody > tr")
        divunits = []
        for tr in trs:
            yearmonth = tr.select_one("th").get_text().strip()
            amount = tr.select_one("td").get_text().strip()

            # 「予」記号への対応
            ym = yearmonth.strip("予 ※").split(".")

            # 「万」の対応
            amount = amount.replace("万", "000")

            # 「～」= 配当金額幅への対応。少額を採用
            wave_pos = amount.find("～")
            if wave_pos != -1:
                amount = amount[:wave_pos]

            divunit = Divunit(
                ticker, date(int("20" + ym[0]), int(ym[1]), 1), Decimal(amount), False if "予" in yearmonth else True
            )
            divunits.append(divunit)

        return divunits
