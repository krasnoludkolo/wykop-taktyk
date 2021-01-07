import os
import time
import logging
from typing import NoReturn, Tuple
from wykop import WykopAPI

from ReminderRepository import ShelveReminderRepository
from TaktykBot import TaktykBot

KEYS_FILE_NAME = 'keys'


def main_loop(bot: TaktykBot):
    logging.info('start main loop')
    bot.save_new_reminders()
    bot.send_reminders()
    logging.info('end main loop')
    time.sleep(1)


def main() -> NoReturn:
    api = create_wykop_api()
    bot = TaktykBot(api, ShelveReminderRepository('test_db'))
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    while True:
        main_loop(bot)
        time.sleep(1)


def read_keys_from_file() -> Tuple[str, ...]:
    with open(KEYS_FILE_NAME) as f:
        return tuple(f.readline().split())


def read_keys_from_envs() -> Tuple[str, str, str]:
    key = os.environ.get('WYKOP_TAKTYK_KEY')
    secret = os.environ.get('WYKOP_TAKTYK_SECRET')
    account_key = os.environ.get('WYKOP_TAKTYK_ACCOUNTKEY')
    return key, secret, account_key


def create_wykop_api():
    if os.path.isfile(KEYS_FILE_NAME):
        key, secret, account_key = read_keys_from_file()
    else:
        key, secret, account_key = read_keys_from_envs()
    api = WykopAPI(key, secret, account_key=account_key)
    api.authenticate()
    return api


main()
