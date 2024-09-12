from logging import getLogger

from domain.model.valuation import Valuation, ValuationIn
from infrastructure.valuation.source_page import SourcePage
from infrastructure.valuation.valuation_gs import ValuationGs

log = getLogger(__name__)


class ValuationRepository:
    def __init__(self) -> None:
        self._gs = ValuationGs()

    def retrieve(self) -> list[Valuation]:
        # 対象ティッカーを取得
        valuation_ins: list[ValuationIn] = self._gs.get_tickers()
        log.info("targets: %s", valuation_ins)

        # バリュエーションデータを収集
        source_page = SourcePage()
        return source_page.collect_valuation(valuation_ins)

    def save(self, valuations: list[Valuation]) -> None:
        self._gs.write_valuations(valuations)
