from typing import NoReturn
import os
from wykop import WykopAPIv2


def main() -> NoReturn:
    key = os.environ.get('WYKOP_TAKTYK_KEY')
    secret = os.environ.get('WYKOP_TAKTYK_SECRET')
    account_key = os.environ.get('WYKOP_TAKTYK_ACCOUNT_KEY')
    api = WykopAPIv2(key, secret, accountkey=account_key)
    api.authenticate()
    print(api.userkey)
    print(api.get_conversations_list())
    print(api.get_notifications())


main()


# content-type: application/x-www-form-urlencoded
# accountkey=cpV14O6dnSp0DCGZ9fUC