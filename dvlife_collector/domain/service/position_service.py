from datetime import date
from logging import getLogger

from domain.model.position import Position
from domain.model.position_by_bank import PositionByBank
from infrastructure.position_repository import PositionRepository

log = getLogger(__name__)


class PositionService:
    def __init__(self):
        # TODO 依存性逆転→DI
        self.__position_repository = PositionRepository()

    def renew(self) -> None:
        # 最新のポジションをスクレイピング
        positions_by_bank: list[PositionByBank] = self.__position_repository.retrieve_all_by_bank()

        # 銘柄ごとの集約
        positions: list[Position] = self.__sum_by_stock(positions_by_bank)

        # 保存
        self.__position_repository.save(positions)

    def __sum_by_stock(self, positions_by_bank: list[PositionByBank]) -> list[Position]:
        base_date = date.today()
        positions_by_ticker = {}
        # TODO 一旦ゴリ押しで
        for elem in positions_by_bank:
            position: Position = positions_by_ticker.get(elem.ticker)
            if position is None:
                position = Position(
                    elem.ticker.ticker, base_date, elem.quantity, elem.acquisition_price, elem.current_price
                )
            else:
                position = position.add(elem)
            positions_by_ticker[elem.ticker] = position

        return list(positions_by_ticker.values())
