# import numpy as np
# from constant.constants import POSITION_IN
# from domain.model.ticker import Ticker
from domain.service.position_service import PositionService


class CollectUseCase:
    def __init__(self):
        self.__position_service = PositionService()

    def renew(self):
        # # 対象ティッカーを読み込み
        # target_stocks = np.loadtxt(POSITION_IN, delimiter=",", dtype=str)
        # tickers = []
        # for stock in target_stocks:
        #     ticker: Ticker = Ticker(stock)
        #     tickers.append(ticker)

        # # メイン
        self.__position_service.renew()
