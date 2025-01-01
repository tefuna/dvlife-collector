import os
import time
from datetime import datetime
from decimal import Decimal
from logging import getLogger

from bs4 import BeautifulSoup
from domain.model.valuation import Valuation, ValuationIn
from exception.webload_exception import WebloadException
from lxml import html
from retry import retry
from selenium import webdriver
from selenium.webdriver.common.by import By

log = getLogger(__name__)


class SourcePage:
    def __init__(self) -> None:
        # webdriver settings
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1200x600")
        options.add_argument("disable-popup-blocking")
        options.add_argument("--incognito")
        self.driver = webdriver.Remote(command_executor="http://selenium_chrome:4444/wd/hub", options=options)
        self.driver.implicitly_wait(5)

    def collect_valuation(self, valuation_ins: list[ValuationIn]) -> list[Valuation]:
        try:
            self._move_to_target_page()
            valuations: list[Valuation] = self._parse(valuation_ins)
        finally:
            self.driver.quit()
        return valuations

    def _move_to_target_page(self) -> None:
        # ログイン
        self.driver.get(os.environ["SBI_URL"])
        self.driver.find_element(By.NAME, "user_id").send_keys(os.environ["SBI_USER"])
        self.driver.find_element(By.NAME, "user_password").send_keys(os.environ["SBI_PASS"])
        self.driver.find_element(By.NAME, "ACT_login").click()

        # ダミーで検索して画面遷移
        self.driver.find_element(By.ID, "top_stock_sec").send_keys("dummy")
        self.driver.find_element(By.XPATH, '//*[@id="srchK"]/a').click()
        time.sleep(3)

    def _parse(self, valuation_ins: list[ValuationIn]) -> list[Valuation]:
        valuations: list[Valuation] = []
        for valuation_in in valuation_ins:
            valuations.append(self._parse_by_ticker(valuation_in))
        return valuations

    def _parse_by_ticker(self, valuation_in: ValuationIn) -> Valuation:
        log.info("parse ticker: %s", valuation_in)

        # ティッカーで検索
        self.driver.find_element(By.ID, "top_stock_sec").send_keys(valuation_in.ticker)
        self.driver.find_element(By.XPATH, '//*[@id="srchK"]/a').click()
        time.sleep(0.5)

        # scope に対応する情報を取得（高速化のため）
        valuation: Valuation = self._get_valuation_price(valuation_in)
        if valuation_in.scope == "all":
            valuation = self._append_valuation_hbook(valuation)

        return valuation

    def _get_valuation_price(self, valuation_in: ValuationIn) -> Valuation:
        self._retry_for_load_values('//*[@id="MTB0_0"]/p/em/span[1]')
        html_price = self.driver.page_source.encode("utf-8")
        soup_price = BeautifulSoup(html_price, "html.parser", from_encoding="utf-8")
        lxml_price: html.HtmlElement = html.fromstring(str(soup_price))

        # 株価
        current_price = lxml_price.xpath('//*[@id="MTB0_0"]/p/em/span[1]')[0].text
        current_price = current_price.replace(",", "")
        # 前日比%
        price_changed_rate_the_day_before = lxml_price.xpath('//*[@id="MTB0_1"]/p/span[2]')[0].text
        price_changed_rate_the_day_before = price_changed_rate_the_day_before.replace("％", "")
        # 年初来安値
        price_YTD_low = lxml_price.xpath('//*[@id="clmMainArea"]/div[6]/table/tbody/tr[1]/td[2]/p/span[1]')[0].text
        price_YTD_low = price_YTD_low.replace(",", "")
        # 予EPS
        forward_EPS = lxml_price.xpath('//*[@id="posElem_190"]/table/tbody/tr[1]/td[2]/p')[0].text
        forward_EPS = forward_EPS.replace(",", "")
        # 予PER
        forward_PER = lxml_price.xpath('//*[@id="MTB0_79"]/p/span[1]')[0].text
        forward_PER = forward_PER.replace("倍", "")
        # 実PBR
        actual_PBR = lxml_price.xpath('//*[@id="MTB0_80"]/p/span[1]')[0].text
        actual_PBR = actual_PBR.replace("倍", "")
        # 1株配当
        dividend_per_share = lxml_price.xpath('//*[@id="posElem_190"]/table/tbody/tr[3]/td[2]/p')[0].text
        wave_pos = dividend_per_share.find("～")
        if wave_pos != -1:
            dividend_per_share = dividend_per_share[:wave_pos]
        # 配当利回り
        dividend_yield = lxml_price.xpath('//*[@id="MTB0_81"]/p/span[1]')[0].text
        dividend_yield = dividend_yield.replace("％", "")

        return Valuation(
            valuation_in,
            datetime.now(),
            Decimal(current_price),
            Decimal(price_changed_rate_the_day_before) / 100,
            Decimal(price_YTD_low),
            Decimal(forward_EPS),
            Decimal(forward_PER),
            Decimal(actual_PBR),
            Decimal(dividend_per_share),
            Decimal(dividend_yield) / 100,
        )

    def _append_valuation_hbook(self, valuation_price: Valuation) -> Valuation:
        self.driver.find_element(
            By.XPATH, '//*[@id="main"]/form[2]/div[3]/div/div/table/tbody/tr[1]/td[5]/span/a'
        ).click()
        self.driver.find_element(By.XPATH, '//*[@id="main"]/div[7]/div/ul/li[2]/p/a').click()
        html_hbook = self.driver.page_source.encode("utf-8")
        soup_hbook = BeautifulSoup(html_hbook, "html.parser", from_encoding="utf-8")
        lxml_hbook: html.HtmlElement = html.fromstring(str(soup_hbook))

        # 自己資本比率
        equity_ratio = lxml_hbook.xpath('//*[@id="main"]/div[8]/table[3]/tbody/tr/td[3]/table/tbody/tr[4]/td[2]')[
            0
        ].text
        equity_ratio = equity_ratio.replace(r"%", "").strip()
        # 実ROE
        actual_ROE = lxml_hbook.xpath('//*[@id="main"]/div[8]/table[3]/tbody/tr/td[1]/table[1]/tbody/tr[12]/td[2]')[
            0
        ].text
        actual_ROE = actual_ROE.replace(r"%", "").strip()
        actual_ROE = "0" if actual_ROE == "‥" else actual_ROE
        # 予ROE
        forward_ROE = lxml_hbook.xpath('//*[@id="main"]/div[8]/table[3]/tbody/tr/td[1]/table[1]/tbody/tr[12]/td[3]')[
            0
        ].text
        forward_ROE = forward_ROE.replace("予", "").replace(r"%", "").strip()
        # 実ROA
        actual_ROA = lxml_hbook.xpath('//*[@id="main"]/div[8]/table[3]/tbody/tr/td[1]/table[1]/tbody/tr[13]/td[2]')[
            0
        ].text
        actual_ROA = actual_ROA.replace(r"%", "").strip()
        actual_ROA = "0" if actual_ROA == "‥" else actual_ROA
        # 予ROA
        forward_ROA = lxml_hbook.xpath('//*[@id="main"]/div[8]/table[3]/tbody/tr/td[1]/table[1]/tbody/tr[13]/td[3]')[
            0
        ].text
        forward_ROA = forward_ROA.replace("予", "").replace(r"%", "").strip()
        # 実EPS
        actual_EPS = lxml_hbook.xpath('//*[@id="main"]/div[8]/table[3]/tbody/tr/td[1]/table[1]/tbody/tr[14]/td[2]')[
            0
        ].text
        actual_EPS = actual_EPS.replace(",", "").replace("円", "").strip()
        actual_EPS = "0" if actual_EPS == "―" else actual_EPS

        return Valuation(
            valuation_price.valuation_in,
            valuation_price.last_updated,
            valuation_price.current_price,
            valuation_price.price_changed_rate_the_day_before,
            valuation_price.price_YTD_low,
            valuation_price.forward_EPS,
            valuation_price.forward_PER,
            valuation_price.actual_PBR,
            valuation_price.dividend_per_share,
            valuation_price.dividend_yield,
            Decimal(equity_ratio) / 100,
            Decimal(actual_ROE) / 100,
            Decimal(forward_ROE) / 100,
            Decimal(actual_ROA) / 100,
            Decimal(forward_ROA) / 100,
            Decimal(actual_EPS),
        )

    @retry(exceptions=Exception, tries=4, delay=1)
    def _retry_for_load_values(self, xpath: str) -> None:
        current_price_elem = self.driver.find_element(By.XPATH, xpath)
        if current_price_elem is None or current_price_elem.text == "--":
            raise WebloadException(f"cannot get current price value. xpath: {xpath}")
