import os
from logging import getLogger

import gspread
from domain.model.valuation import Valuation, ValuationIn
from gspread.exceptions import APIError
from gspread.utils import ValueInputOption
from retry import retry

log = getLogger(__name__)


class ValuationGs:
    def __init__(self) -> None:
        gc = gspread.oauth(credentials_filename=os.environ["VALU_GS_AUTH"])
        self._worksheet = gc.open_by_url(os.environ["VALU_GS_URL"]).worksheet(os.environ["VALU_GS_SHEET"])

    def get_tickers(self) -> list[ValuationIn]:
        ins: list[ValuationIn] = []
        range_cells: list[list[str]] = self._worksheet.get(os.environ["VALU_GS_CELL_TARGET"])
        for row in range_cells:
            # 「含む」 = "o" が対象
            if len(row) > 3 and row[0] == "o":
                valuation_in = ValuationIn(row[4], row[1], int(row[2]))
                ins.append(valuation_in)
        return ins

    def write_valuations(self, valuations: list[Valuation]) -> None:
        updates: list[list[str]] = []
        for elem in valuations:
            log.info("write spreadsheet. ticker: %s", elem.valuation_in.ticker)
            updates.clear()
            updates.append(elem.to_list4gs_all() if elem.valuation_in.scope == "all" else elem.to_list4gs_price())
            self._retry_write_row_to_worksheet(updates, elem.valuation_in.row_number)

    @retry(exceptions=APIError, tries=2, delay=60)
    def _retry_write_row_to_worksheet(self, updates: list[list[str]], row_number: int) -> None:
        self._worksheet.update(
            updates,
            os.environ["VALU_GS_COL_UPDATES"] + str(row_number),
            value_input_option=ValueInputOption.user_entered,
        )
