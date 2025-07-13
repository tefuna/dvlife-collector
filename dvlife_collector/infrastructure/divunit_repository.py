import os
from pathlib import Path

import pandas
from constant.site_kind import SiteKind
from domain.model.annual_dividend import AnnualDividend
from domain.model.divunit import Divunit
from domain.model.divunit_target import DivunitTarget
from infrastructure.credential import Credential
from infrastructure.divunit.page.jp_etf_page import JpEtfPage
from infrastructure.divunit.page.jp_normal_page import JpNormalPage
from infrastructure.divunit.page.us_etf_page import UsEtfPage
from infrastructure.divunit.page.us_normal_page import UsNormalPage


class DivunitRepository:
    def __init__(self) -> None:
        pass

    def retrieve_divunit(self, targets: list[DivunitTarget]) -> list[Divunit]:
        # SiteKindごとに区分け
        targets_by_site = self._split_by_site(targets)
        divunits = []

        # JP_NORMAL
        cred = Credential(os.environ["RAK_USER"], os.environ["RAK_PASS"])
        jp_normal_page = JpNormalPage(cred)
        divunits.extend(jp_normal_page.scrape(targets_by_site[SiteKind.JP_NORMAL]))

        # JP_ETF
        jp_etf_page = JpEtfPage(cred)
        divunits.extend(jp_etf_page.scrape(targets_by_site[SiteKind.JP_ETF]))

        # TODO https://github.com/tefuna/dvlife-collector/issues/37
        # # US_NORMAL
        # us_normal_page = UsNormalPage(None)
        # divunits.extend(us_normal_page.scrape(targets_by_site[SiteKind.US_NORMAL]))

        # # US_ETF
        # us_etf_page = UsEtfPage(None)
        # divunits.extend(us_etf_page.scrape(targets_by_site[SiteKind.US_ETF]))

        return divunits

    def _split_by_site(self, targets: list[DivunitTarget]) -> dict[SiteKind, list[DivunitTarget]]:
        targets_by_site = {}
        for kind in SiteKind:
            targets_by_site[kind] = list(filter(lambda target: target.site_kind == kind, targets))
        return targets_by_site

    def save(self, divunits: list[Divunit]) -> None:
        out_dir = os.environ["DIVUNIT_OUT_DIR"]
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        sorted_list = sorted(divunits, key=lambda divunit: divunit.divunit_id)
        df = pandas.DataFrame(sorted_list)
        df.to_csv(f"{out_dir}/divunit_out.csv", sep="\t", index=False, header=False)

    def save_annual(self, annual_divs: list[AnnualDividend]) -> None:
        out_dir = os.environ["DIVUNIT_OUT_DIR"]
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        sorted_list = sorted(annual_divs, key=lambda x: x.ticker)
        df = pandas.DataFrame(sorted_list)
        df.to_csv(f"{out_dir}/annual_dividend.csv", columns=["ticker", "amount"], sep="\t", index=False, header=False)
