from logging import config, getLogger

import yaml
from application.position_collect_usecase import PositionCollectUseCase
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
    collect_usecase = PositionCollectUseCase()
    collect_usecase.renew()


if __name__ == "__main__":
    main()
