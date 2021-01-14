import os
import time
import logging
from typing import NoReturn, Tuple, List
from wykop import WykopAPI, MultiKeyWykopAPI

from ReminderRepository import ShelveReminderRepository
from TaktykBot import TaktykBot
from argparse import ArgumentParser

KEYS_FILE_NAME = 'keys'
WYKOP_APP_KEY = 'aNd401dAPp'
BASE_DIR = os.getcwd()
# TODO move into ./log/ (create if not dir not exists)
LOG_FILE = f'{BASE_DIR}/wykop-taktyk.log'
# TODO move into ./db/ (create if not dir not exists)
REPOSITORY_DIR = f'{BASE_DIR}/reminders.db'


def main_loop(bot: TaktykBot):
    logging.info('start main loop')
    bot.save_new_reminders()
    bot.send_reminders()
    logging.info('end main loop')


def main() -> NoReturn:
    use_login_and_password = load_program_args(create_argument_parser())
    api = create_wykop_api(use_login_and_password)
    bot = TaktykBot(api, ShelveReminderRepository(REPOSITORY_DIR))
    # TODO INFO -> console, DEBUG -> file
    logging.basicConfig(
        # filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    while True:
        main_loop(bot)
        # TODO use program args
        time.sleep(1)


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("-l", default=False, dest='use_login_and_password', action='store_true',
                        help="Force to use login and password authenticate")
    return parser


def load_program_args(parser: ArgumentParser) -> bool:
    args = parser.parse_args()
    return args.use_login_and_password


def read_keys_from_file() -> List[List[str]]:
    with open(KEYS_FILE_NAME) as f:
        return [line.split() for line in f.readlines()]


def read_login_and_password() -> Tuple[str, str]:
    login = os.environ.get('WYKOP_TAKTYK_BOT_LOGIN')
    password = os.environ.get('WYKOP_TAKTYK_BOT_PASSWORD')
    return login, password


def create_wykop_api(use_login_and_password: bool) -> WykopAPI:
    if os.path.isfile(KEYS_FILE_NAME) and not use_login_and_password:
        keys = read_keys_from_file()
        api = MultiKeyWykopAPI(keys)
    else:
        login, password = read_login_and_password()
        api = WykopAPI(WYKOP_APP_KEY)
        api.authenticate(login=login, password=password)
    return api


main()
