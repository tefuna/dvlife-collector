from itertools import groupby
from logging import getLogger

from dateutil.relativedelta import relativedelta
from domain.model.annual_dividend import AnnualDividend
from domain.model.divunit import Divunit
from domain.model.divunit_target import DivunitTarget
from infrastructure.divunit_repository import DivunitRepository

log = getLogger(__name__)


class DivunitService:
    def __init__(self) -> None:
        # TODO 依存性逆転→DI
        self.__divunit_repository = DivunitRepository()

    def collect(self, targets: list[DivunitTarget]) -> None:
        # 配当履歴取得
        divunits = self.__divunit_repository.retrieve_divunit(targets)

        # 保存
        self.__divunit_repository.save(divunits)

        # 銘柄ごとの年間配当を算出
        annual_divs = self.__calc_annual_dividens(divunits)
        self.__divunit_repository.save_annual(annual_divs)

    def __calc_annual_dividens(self, divunits: list[Divunit]) -> list[AnnualDividend]:
        sorted_divunits = sorted(divunits, key=lambda x: x.divunit_id, reverse=True)

        # tickerごとに集計
        annual_divs = []
        for ticker, g in groupby(sorted_divunits, key=lambda x: x.ticker):
            divunits_by_ticker = list(g)
            latest_div_date = divunits_by_ticker[0].div_date
            tmp_divs = []
            for divunit in divunits_by_ticker:
                if divunit.div_date <= latest_div_date + relativedelta(months=-11, days=-15):
                    # 最新の配当単位から11.5ヶ月のものを集計対象に
                    break
                tmp_divs.append(divunit)
            annual_div = AnnualDividend(ticker, tmp_divs)
            annual_divs.append(annual_div)

        return annual_divs
