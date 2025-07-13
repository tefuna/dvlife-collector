import os
import time
from decimal import Decimal
from logging import getLogger

from bs4 import BeautifulSoup, ResultSet, Tag
from constant.bank import Bank
from domain.model.position_by_bank import PositionByBank
from domain.model.ticker import Ticker
from infrastructure.position.page.page_base import PageBase
from selenium.webdriver.common.by import By

log = getLogger(__name__)

KINDS = {
    "jp": "国内株式",
    "us": "米国株式",
}


class RakutenPage(PageBase):
    def _move_to_target_page(self) -> None:
        # ログイン + 多要素認証入力
        self.driver.get(os.environ["RAK_URL"])
        self.driver.find_element(By.ID, "form-login-id").send_keys(self._credential.username)
        self.driver.find_element(By.ID, "form-login-pass").send_keys(self._credential.password)
        self.driver.find_elements(By.CLASS_NAME, "s3-form-login__btn")[0].click()

        # 保有商品一覧へ遷移
        self.driver.find_element(
            By.XPATH, '//*[@id="str-container"]/div[2]/main/form[2]/div[3]/div[1]/div[1]/div[2]/div[1]/a[1]'
        ).click()
        time.sleep(5)

        # html parse
        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # trタグのリスト
        self._target_tags = soup.select("#table_possess_data > span > table > tbody > tr")

    def _parse(self) -> list[PositionByBank]:
        positions = []

        for i, tr in enumerate(self._target_tags):
            tds = tr.select("td")
            kind = tds[0].get_text().strip()

            # TODO 分岐をやめる。interfaceに
            if kind == KINDS["jp"]:
                positions.append(self._get_position_jp(tds))
            elif kind == KINDS["us"]:
                positions.append(self._get_position_us(tds))
            else:
                log.info("unsupported kind: idx=%d, value=%s", i, kind)
                continue

        return positions

    def _get_position_jp(self, tds: ResultSet[Tag]) -> PositionByBank:
        ticker = tds[1].get_text().strip()
        quantity = tds[7].select_one("a").get_text().replace(",", "").replace("株", "").strip()
        a_price = tds[8].get_text().replace(",", "").replace("円", "").strip()
        c_price = tds[9].select("div")[0].get_text().replace(",", "").replace("円", "").strip()
        position = PositionByBank(Ticker(ticker), Bank.RAKUTEN, int(quantity), Decimal(a_price), Decimal(c_price))
        return position

    def _get_position_us(self, tds: ResultSet[Tag]) -> PositionByBank:
        ticker = tds[1].get_text().strip()
        quantity = tds[4].get_text().replace(",", "").replace("株", "").strip()
        a_price = tds[5].get_text().replace(",", "").replace("USD", "").strip()
        c_price = tds[6].select("div")[0].get_text().replace(",", "").replace("USD", "").strip()
        position = PositionByBank(Ticker(ticker), Bank.RAKUTEN, int(quantity), Decimal(a_price), Decimal(c_price))
        return position
