import logging
import signal
import sys
import time
from argparse import ArgumentParser
from typing import NoReturn, Tuple, List

from wykop import WykopAPI, MultiKeyWykopAPI, WykopAPIError

from taktyk.ApiClientWrapper import ApiClientWrapper
from taktyk.base_logger import logger, add_console_logger, add_file_logger, add_error_file_logger
from taktyk.config import *
from taktyk.observation_repository import ShelveObservationRepository
from taktyk.taktyk_bot import TaktykBot


def main_loop(bot: TaktykBot):
    logger.debug('start main loop')
    bot.run()
    logger.debug('end main loop')


def create_dirs():
    if not os.path.isdir(LOG_DIR):
        logger.debug(f'Creating log dir in:{LOG_DIR}')
        os.mkdir(LOG_DIR)
        logger.debug('Created')
    if not os.path.isdir(REPOSITORY_DIR):
        logger.debug(f'Creating repo dir in:{REPOSITORY_DIR}')
        os.mkdir(REPOSITORY_DIR)
        logger.debug('Created')


def main() -> NoReturn:
    use_login_and_password, interval, console_logging_level = load_program_args(create_argument_parser())
    logger.debug('Program arguments loaded and parsed')
    create_dirs()
    add_console_logger(console_logging_level)
    add_file_logger(LOG_FILE, logging.DEBUG)
    add_error_file_logger(ERROR_LOG_FILE)
    api = create_wykop_api(use_login_and_password)
    bot = TaktykBot(api, ShelveObservationRepository(REPOSITORY_FILE))
    logger.debug('Setup done')
    while True:
        try:
            main_loop(bot)
        except WykopAPIError as e:
            logger.error(f'Wykop API error during main_loop: {type(e)}')
        except Exception as e:
            logger.error(f'Error during main_loop: {e}', exc_info=True)
            bot.api = create_wykop_api(use_login_and_password)
        time.sleep(interval)


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("-l", default=False, dest='use_login_and_password', action='store_true',
                        help="Force to use login and password authenticate")
    parser.add_argument("-i", default=15, dest='interval', type=float,
                        help="Update interval in s")
    parser.add_argument('-d', action='store_true', help='Set DEBUG logging level for console output')

    return parser


def load_program_args(parser: ArgumentParser) -> Tuple[bool, float, int]:
    args = parser.parse_args()
    if args.d:
        level = logging.DEBUG
    else:
        level = logging.INFO
    return args.use_login_and_password, args.interval, level


def read_keys_from_file() -> List[List[str]]:
    with open(KEYS_FILE_NAME) as f:
        return [line.split() for line in f.readlines()]


def read_login_and_password() -> Tuple[str, str]:
    login = os.environ.get('WYKOP_TAKTYK_BOT_LOGIN')
    password = os.environ.get('WYKOP_TAKTYK_BOT_PASSWORD')
    return login, password


def create_wykop_api(use_login_and_password: bool) -> WykopAPI:
    logger.debug(f'creating WykopAPI. use_login_and_password={use_login_and_password}')
    if os.path.isfile(KEYS_FILE_NAME) and not use_login_and_password:
        keys = read_keys_from_file()
        api = MultiKeyWykopAPI(keys)
    else:
        login, password = read_login_and_password()
        api = ApiClientWrapper(WYKOP_APP_KEY, output='clear')
        api.authenticate(login=login, password=password)
    return api


def signal_handler(sig, frame):
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()
