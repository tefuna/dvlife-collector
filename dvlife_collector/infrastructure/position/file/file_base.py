import os
from decimal import Decimal
from logging import getLogger

import pandas
from constant.bank import Bank
from domain.model.position_by_bank import PositionByBank
from domain.model.ticker import Ticker

log = getLogger(__name__)


class FileBase:
    def retrieve_from_file(self) -> list[PositionByBank]:
        positions = []

        log.info("read other_positions.csv")
        df = pandas.read_csv(f"{os.environ['POSITION_IN_DIR']}/other_positions.csv")

        log.debug("other_positions.csv: %s", df)
        for row in df.itertuples():
            position = PositionByBank(Ticker(str(row[1])), Bank.OTHER, int(row[2]), Decimal(row[3]), Decimal(row[4]))
            positions.append(position)
        return positions
