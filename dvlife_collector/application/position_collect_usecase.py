from domain.service.position_service import PositionService


class PositionCollectUseCase:
    def __init__(self) -> None:
        self.__position_service = PositionService()

    def renew(self) -> None:
        # メイン
        self.__position_service.renew()
