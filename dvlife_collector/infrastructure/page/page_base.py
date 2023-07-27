from abc import ABCMeta, abstractmethod

from domain.model.position_by_bank import PositionByBank
from infrastructure.page.credential import Credential
from selenium import webdriver


class PageBase(metaclass=ABCMeta):
    def __init__(self, credential: Credential):
        self._credential = credential

        # webdriver settings
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1200x600")
        options.add_argument("disable-popup-blocking")
        options.add_argument("--incognito")
        self.driver = webdriver.Remote(command_executor="http://selenium_chrome:4444/wd/hub", options=options)
        self.driver.implicitly_wait(5)

    def scrape(self) -> list[PositionByBank]:
        try:
            self._move_to_target_page()
        finally:
            self.driver.quit()
        return self._parse()

    @abstractmethod
    def _move_to_target_page(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _parse(self) -> list[PositionByBank]:
        raise NotImplementedError()
