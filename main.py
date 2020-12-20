import os
import time

from typing import NoReturn
from wykop import WykopAPI

from ReminderRepository import InMemoryReminderRepository
from TaktykBot import TaktykBot


def main() -> NoReturn:
    key = os.environ.get('WYKOP_TAKTYK_KEY')
    secret = os.environ.get('WYKOP_TAKTYK_SECRET')
    account_key = os.environ.get('WYKOP_TAKTYK_ACCOUNTKEY')
    api = WykopAPI(key, secret, account_key=account_key)
    api.authenticate()

    bot = TaktykBot(api, InMemoryReminderRepository())

    while True:
        print("elo")
        bot.save_new_reminders()
        bot.send_reminders()
        time.sleep(5)

main()
