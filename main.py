import os

from typing import NoReturn
from wykop import WykopAPI


def main() -> NoReturn:
    key = os.environ.get('WYKOP_TAKTYK_KEY')
    secret = os.environ.get('WYKOP_TAKTYK_SECRET')
    account_key = os.environ.get('WYKOP_TAKTYK_ACCOUNTKEY')
    api = WykopAPI(key, secret, account_key=account_key)
    api.authenticate()


main()
