from domain.service.position_service import PositionService


class PositionCollectUseCase:
    def __init__(self):
        self.__position_service = PositionService()

    def renew(self):
        # メイン
        self.__position_service.renew()
