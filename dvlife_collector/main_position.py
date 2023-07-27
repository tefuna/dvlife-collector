from logging import config, getLogger

import yaml
from application.position.collect_usecase import CollectUseCase
from constant.constants import LOGGING_CONFIG

# logging
config.dictConfig(
    yaml.load(
        open(LOGGING_CONFIG, encoding="utf-8").read(),
        Loader=yaml.SafeLoader,
    )
)
log = getLogger(__name__)


def main():
    collect_usecase = CollectUseCase()
    collect_usecase.renew()


if __name__ == "__main__":
    main()
