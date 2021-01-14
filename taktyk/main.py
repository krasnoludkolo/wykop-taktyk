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


def main_loop(bot: TaktykBot):
    logging.info('start main loop')
    bot.save_new_reminders()
    bot.send_reminders()
    logging.info('end main loop')


def main() -> NoReturn:
    force_to_use_login_and_password_authentication = load_program_args(create_argument_parser())
    api = create_wykop_api(force_to_use_login_and_password_authentication)
    bot = TaktykBot(api, ShelveReminderRepository('../test_db'))
    logging.basicConfig(
        filename='../wykop-taktyk.log',
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    while True:
        main_loop(bot)
        time.sleep(15)


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("-l", default=False, dest='force_to_use_login_and_password_authentication', action='store_true',
                        help="Force to use login and password authenticate")
    return parser


def load_program_args(parser: ArgumentParser) -> bool:
    args = parser.parse_args()
    return args.force_to_use_login_and_password_authentication


def read_keys_from_file() -> List[List[str]]:
    with open(KEYS_FILE_NAME) as f:
        return [line.split() for line in f.readlines()]


def read_login_and_password() -> Tuple[str, str]:
    login = os.environ.get('WYKOP_TAKTYK_BOT_LOGIN')
    password = os.environ.get('WYKOP_TAKTYK_BOT_PASSWORD')
    return login, password


def create_wykop_api(force_to_use_login_and_password_authentication: bool) -> WykopAPI:
    if os.path.isfile(KEYS_FILE_NAME) and not force_to_use_login_and_password_authentication:
        keys = read_keys_from_file()
        api = MultiKeyWykopAPI(keys)
    else:
        login, password = read_login_and_password()
        api = WykopAPI(WYKOP_APP_KEY)
        api.authenticate(login=login, password=password)
    return api


main()
