import os
import time
import logging
from typing import NoReturn
from wykop import WykopAPI

from ReminderRepository import ShelveReminderRepository
from TaktykBot import TaktykBot


def main_loop(bot: TaktykBot):
    logging.debug('start main loop')
    bot.save_new_reminders()
    bot.send_reminders()
    logging.debug('end main loop')
    time.sleep(1)


def main() -> NoReturn:
    api = create_wykop_api()
    bot = TaktykBot(api, ShelveReminderRepository('test_db'))
    logging.basicConfig(level=logging.DEBUG)

    while True:
        main_loop(bot)
        time.sleep(1)


def create_wykop_api():
    key = os.environ.get('WYKOP_TAKTYK_KEY')
    secret = os.environ.get('WYKOP_TAKTYK_SECRET')
    account_key = os.environ.get('WYKOP_TAKTYK_ACCOUNTKEY')
    api = WykopAPI(key, secret, account_key=account_key)
    api.authenticate()
    return api


main()
