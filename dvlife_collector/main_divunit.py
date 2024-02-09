from logging import config, getLogger

import yaml
from application.divunit_collect_usecase import DivunitCollectUseCase
from constant.constants import LOGGING_CONFIG
from dotenv import load_dotenv

load_dotenv()

# logging
config.dictConfig(
    yaml.load(
        open(LOGGING_CONFIG, encoding="utf-8").read(),
        Loader=yaml.SafeLoader,
    )
)
log = getLogger(__name__)


def main() -> None:
    collect_usecase = DivunitCollectUseCase()
    collect_usecase.renew()


if __name__ == "__main__":
    main()
