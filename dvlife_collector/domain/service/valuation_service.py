from logging import getLogger

from domain.model.valuation import Valuation
from infrastructure.valuation_repository import ValuationRepository

log = getLogger(__name__)


class ValuationService:
    def __init__(self) -> None:
        # TODO 依存性逆転→DI
        self.__valuation_repository = ValuationRepository()

    def update(self)-> list[Valuation]:
        valuations: list[Valuation] = self.__valuation_repository.retrieve()
        self.__valuation_repository.save(valuations)
