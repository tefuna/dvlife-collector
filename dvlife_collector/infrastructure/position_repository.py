import os
from pathlib import Path

import pandas
from domain.model.position import Position
from domain.model.position_by_bank import PositionByBank
from infrastructure.credential import Credential
from infrastructure.position.file.file_base import FileBase
from infrastructure.position.page.rakuten_page import RakutenPage
from infrastructure.position.page.sbi_page import SbiPage


class PositionRepository:
    def __init__(self) -> None:
        pass

    def retrieve_all_by_bank(self) -> list[PositionByBank]:
        positions_by_bank = []
        positions_by_bank.extend(self._retrieve_rakuten())
        positions_by_bank.extend(self._retrieve_sbi())
        positions_by_bank.extend(self._retrieve_others_from_file())
        return positions_by_bank

    def _retrieve_rakuten(self) -> list[PositionByBank]:
        username = os.environ["RAK_USER"]
        password = os.environ["RAK_PASS"]
        cred = Credential(username, password)
        return RakutenPage(cred).scrape()  # type: ignore

    def _retrieve_sbi(self) -> list[PositionByBank]:
        username = os.environ["SBI_USER"]
        password = os.environ["SBI_PASS"]
        cred = Credential(username, password)
        return SbiPage(cred).scrape()  # type: ignore

    def _retrieve_others_from_file(self) -> list[PositionByBank]:
        return FileBase().retrieve_from_file()

    def save(self, positions: list[Position]) -> None:
        out_dir = os.environ["POSITION_OUT_DIR"]
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        sorted_pos = sorted(positions, key=lambda position: (position.ticker, position.base_date))
        df = pandas.DataFrame(sorted_pos)
        df.to_csv(f"{out_dir}/position_out.csv", sep="\t", index=False, header=False)
