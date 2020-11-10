from typing import NoReturn
import os
from wykop import WykopAPIv2


def main() -> NoReturn:
    key = os.environ.get('WYKOP_TAKTYK_KEY')
    secret = os.environ.get('WYKOP_TAKTYK_SECRET')
    api = WykopAPIv2(key, secret, output='clear')
    params = api.get_default_api_params()
    api.authenticate("krasnoludkolo", accountkey="")


main()
