from domain.service.position_service import PositionService


class PositionCollectUseCase:
    def __init__(self) -> None:
        self._position_service = PositionService()

    def renew(self) -> None:
        # メイン
        self._position_service.renew()
