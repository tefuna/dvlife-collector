from abc import ABCMeta, abstractmethod

from domain.model.divunit import Divunit
from domain.model.divunit_target import DivunitTarget
from infrastructure.credential import Credential
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

    def scrape(self, targets: list[DivunitTarget]) -> list[Divunit]:
        try:
            if len(targets) == 0:
                return []
            divunits = self._retrieve(targets)
        finally:
            self.driver.quit()
        return divunits

    @abstractmethod
    def _retrieve(self, targets: list[DivunitTarget]) -> list[Divunit]:
        raise NotImplementedError()
