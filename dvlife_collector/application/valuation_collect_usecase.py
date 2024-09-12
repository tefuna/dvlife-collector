from domain.service.valuation_service import ValuationService


class ValuationCollectUseCase:
    def __init__(self) -> None:
        self._valuation_service = ValuationService()

    def renew(self) -> None:
        # メイン
        self._valuation_service.update()
