import logging

from wykop import WykopAPI
from wykop.api.exceptions import ReceiverHasBlockedDMError

from taktyk.wykop_api_utils import entry_url


class MessageSender:
    def __init__(self, api: WykopAPI):
        self.api: WykopAPI = api

    def __send_message(self, login, message) -> None:
        logging.info(f'send message to: {login}. Message: {message}')
        self.api.message_send(login, message)

    def send_new_comment_message(self, last_seen_comment_id: str, login: str, entry_id: str) -> None:
        try:
            message = f'nowy komentarz {entry_url}/{entry_id}#comment-{last_seen_comment_id}'
            self.__send_message(login, message)
        except ReceiverHasBlockedDMError:
            logging.info(f'Error during sending message to {login}')

    def send_removed_observation_message(self, login, entry_ids_from_removed_observations) -> None:
        message = f'Usunięto: {"".join(entry_ids_from_removed_observations)}'
        self.__send_message(login, message)

    def send_no_observation_to_remove_message(self, login) -> None:
        message = 'Nic do usunięcia'
        self.__send_message(login, message)
