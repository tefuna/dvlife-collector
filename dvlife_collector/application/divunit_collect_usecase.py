import os

import pandas
from constant.site_kind import SiteKind
from domain.model.divunit_target import DivunitTarget
from domain.service.divunit_service import DivunitService


class DivunitCollectUseCase:
    def __init__(self):
        self.__divunit_service = DivunitService()

    def renew(self):
        # 対象取得
        df = pandas.read_csv(os.environ["DIVUNIT_IN_DIR"] + "/target_tickers.csv", header=None, dtype=str)
        targets = []
        for row in df.itertuples():
            target = DivunitTarget(row[1], SiteKind(row[2]), row[3])
            targets.append(target)
        sorted_targets = sorted(targets, key=lambda t: t.ticker)

        # メイン
        self.__divunit_service.collect(sorted_targets)
