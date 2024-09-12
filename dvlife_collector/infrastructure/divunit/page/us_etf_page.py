import time
from datetime import date, datetime
from decimal import Decimal

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from domain.model.divunit import Divunit
from domain.model.divunit_target import DivunitTarget
from infrastructure.divunit.page.page_base import PageBase
from selenium.webdriver.common.by import By


class UsEtfPage(PageBase):
    def _retrieve(self, targets: list[DivunitTarget]) -> list[Divunit]:
        divunits = []
        for target in targets:
            divunits.extend(self._parse(target))

        return divunits

    def _parse(self, target: DivunitTarget) -> list[Divunit]:
        self.driver.get(target.url)
        self.driver.find_element(By.XPATH, '//*[@id="distributions"]/div/div[2]/div[2]/div/a').click()
        time.sleep(3)

        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        divunits = self._get_divunit(target.ticker, soup)
        return divunits

    def _get_divunit(self, ticker: str, soup: BeautifulSoup) -> list[Divunit]:
        trs = soup.select("#distributions > div > div.row > div.col-lg-4.col-md-6 > div > table > tbody > tr")
        divunits = []
        for tr in trs:
            tds = tr.select("td")

            # paid_dateしか取れないため、これをdiv_dateとして扱う
            div_date_str = tds[0].get_text().strip()
            div_date = datetime.strptime(div_date_str, "%b %d, %Y").date()
            amount = tds[1].get_text().strip().strip("$").strip()

            divunit = Divunit(ticker, div_date, Decimal(amount), True if div_date < date.today() else False)
            divunits.append(divunit)

        return divunits

    def _get_future_divs(self, divunits: list[Divunit]) -> list[Divunit]:
        # TODO Quarterlyのみ対応
        # last_year_divunits = list(
        #     filter(lambda divunit: divunit.div_date > date.today() - relativedelta(years=1), divunits)
        # )

        future_divs = []
        for last_div in divunits[:4]:
            future_div = Divunit(last_div.ticker, last_div.div_date + relativedelta(years=1), last_div.amount, False)
            future_divs.append(future_div)

        # TODO どんなデータがあるか不明のため、あとで気づく用
        if len(future_divs) != 4:
            raise ValueError(f"Invalid future_divs: {future_divs}")

        return future_divs
