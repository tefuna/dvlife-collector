from datetime import datetime
from decimal import Decimal
from logging import getLogger

from bs4 import BeautifulSoup
from bs4.element import Tag
from domain.model.divunit import Divunit
from domain.model.divunit_target import DivunitTarget
from infrastructure.divunit.page.page_base import PageBase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

log = getLogger(__name__)

URL = {
    "login": "https://www.rakuten-sec.co.jp/",
}


class JpEtfPage(PageBase):
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

        # 配当ページのhtml取得
        self.driver.find_element(
            By.XPATH,
            '//*[@id="auto_update_field_info_jp_stock_price"]/tbody/tr/td[1]/form[2]/div[2]/table[2]/tbody/tr/td[1]/table/tbody/tr/td/div/div/ul/li[9]/a',  # noqa: E501
        ).click()

        # iframe用の取得
        iframe = self.driver.find_element(By.ID, "J010101-011-1")
        src = iframe.get_attribute("src")
        self.driver.get(src)

        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        return self.__get_divunit(target.ticker, soup)

    def __get_divunit(self, ticker: str, soup: BeautifulSoup) -> list[Divunit]:
        divunits = {}

        # 予想配当情報
        trs = soup.select("#dividend-main > div:nth-child(2) > div:nth-child(2) > table:nth-child(2) > tbody > tr")
        for tr in trs:
            divunit = self.__get_div_row(tr, ticker, False)
            if divunit is not None:
                divunits[divunit.divunit_id] = divunit

        # 確定配当情報
        trs = soup.select("#dividend-main > div:nth-child(2) > div:nth-child(2) > table:nth-child(4) > tbody > tr")
        for tr in trs:
            divunit = self.__get_div_row(tr, ticker, True)
            if divunit is not None:
                divunits[divunit.divunit_id] = divunit

        return list(divunits.values())

    def __get_div_row(self, tr: Tag, ticker: str, paid: bool) -> Divunit | None:
        tds = tr.select("td")
        div_date_str = tds[0].get_text().strip()
        if div_date_str == "-":
            log.info("dividend data row is not assigned: %s", ticker)
            return None
        div_date = datetime.strptime(div_date_str, "%Y/%m/%d").date()
        amount = tds[1].get_text().strip()
        if not amount.isdecimal():
            amount = 0
            log.warn("div amount not determined. ticker: %s, amount: %s", ticker, amount)

        return Divunit(ticker, div_date, Decimal(amount), paid)
