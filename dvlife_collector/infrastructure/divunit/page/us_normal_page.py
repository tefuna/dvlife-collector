import time
from datetime import date, datetime
from decimal import Decimal
from logging import getLogger

from bs4 import BeautifulSoup
from domain.model.divunit import Divunit
from domain.model.divunit_target import DivunitTarget
from infrastructure.divunit.page.page_base import PageBase
from selenium.webdriver.common.by import By

log = getLogger(__name__)

class UsNormalPage(PageBase):
    def _retrieve(self, targets: list[DivunitTarget]) -> list[Divunit]:
        divunits = []

        for target in targets:
            divunits.extend(self._parse(target))

        return divunits

    def _parse(self, target: DivunitTarget) -> list[Divunit]:
        log.debug("parse target: %s", target.ticker)
        self.driver.get(target.url)
        self.driver.find_element(By.CLASS_NAME, "full-screen-payout-history").click()
        time.sleep(3)

        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        divunits = self._get_divunit(target.ticker, soup)
        return divunits

    def _get_divunit(self, ticker: str, soup: BeautifulSoup) -> list[Divunit]:
        trs = soup.select("#full-screen-payout-modal tbody > tr")
        divunits: list[Divunit] = []

        # 配当行なしの場合
        if len(trs) == 1 and trs[0].get_text().find("empty") != -1:
            return divunits

        for tr in trs:
            # 列値の取得
            tds = tr.select("td")
            for td in tds:
                match td.attrs["data-th"]:
                    case "Pay Date":
                        pay_date = datetime.strptime(td.get_text().strip(), "%Y-%m-%d").date()
                    case "Ex-Dividend Date":
                        div_date_str = td.get_text().strip()
                        if div_date_str == "-":
                            # 未指定の場合は、pay_dateと同値とする
                            div_date = pay_date
                        else:
                            div_date = datetime.strptime(div_date_str, "%Y-%m-%d").date()
                    case "Payout Amount (USD)":
                        div_date_str = td.get_text().strip()
                        if div_date_str == "-":
                            # 未指定の場合はゼロとして扱う
                            amount = Decimal(0)
                        else:
                            amount = Decimal(div_date_str.strip("$"))

            divunit = Divunit(ticker, div_date, amount, True if pay_date < date.today() else False)
            divunits.append(divunit)

        return divunits
