import logging

from wykop import WykopAPI
from wykop.api.exceptions import ReceiverHasBlockedDMError

from taktyk.wykop_api_utils import entry_url


class MessageSender:
    def __init__(self, api: WykopAPI):
        self.api: WykopAPI = api

    def __send_message(self, login, message):
        logging.info(f'send message to: {login}. Message: {message}')
        self.api.message_send(login, message)

    def send_reminder_to_login(self, last_seen_comment_id, login, reminder):
        try:
            message = f'nowy komentarz {entry_url}/{reminder.entry_id}#comment-{last_seen_comment_id}'
            self.__send_message(login, message)
        except ReceiverHasBlockedDMError:
            logging.info(f'Error during sending message to {login}')

    def send_removed_reminder_message(self, login, entry_ids_from_removed_reminders):
        message = f'Usunięto: {"".join(entry_ids_from_removed_reminders)}'
        self.__send_message(login, message)

    def send_no_reminder_to_remove_message(self, login):
        message = 'Nic do usunięcia'
        self.__send_message(login, message)
