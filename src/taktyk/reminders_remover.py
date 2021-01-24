import logging
import re
from typing import Optional

from wykop import WykopAPI

from taktyk.message_sender import MessageSender
from taktyk.reminder_repository import ReminderRepository
from taktyk.wykop_api_utils import *


class RemindersRemover:
    def __init__(self, api: WykopAPI, repo: ReminderRepository, message_sender: MessageSender):
        self.api: WykopAPI = api
        self.repo: ReminderRepository = repo
        self.message_sender = message_sender
        self.url_entry_id_pattern = re.compile(r'wpis/\d+')

    def remove_reminders_from_messages(self):
        for conversation_summary in self.api.conversations_list():
            self.__process_conversation(conversation_summary)

    def __process_conversation(self, conversation_summary):
        login = get_login_from_conversation_summary(conversation_summary)
        conversation = self.api.conversation(login)
        if has_new_messages(conversation):
            self.__parse_messages(conversation, login)

    def __parse_messages(self, conversation: Conversation, login: str):
        new_messages = take_new_messages(conversation)
        entry_ids_from_removed_reminders = []
        for message in take_messages_body(new_messages):
            removed_id = self.__remove_reminder_from_message(login, message)
            if removed_id:
                entry_ids_from_removed_reminders += removed_id
        self.__send_summary_to_login(entry_ids_from_removed_reminders, login)

    def __remove_reminder_from_message(self, login, message) -> Optional[str]:
        entry_id = self.__take_entry_id_from_message(message)
        if self.repo.has_reminder_with_login(entry_id, login):
            logging.info(f'Removing {login} from {entry_id}')
            self.repo.remove_login_from_reminder(entry_id, login)
            return entry_id
        return None

    def __send_summary_to_login(self, entry_ids_from_removed_reminders, login):
        if entry_ids_from_removed_reminders:
            self.message_sender.send_removed_reminder_message(login, entry_ids_from_removed_reminders)
        else:
            self.message_sender.send_no_reminder_to_remove_message(login)

    def __take_entry_id_from_message(self, message: str) -> str:
        if message.isdigit():
            return message
        else:
            return str(self.url_entry_id_pattern.findall(message)[0]).split('/')[1]


def has_new_messages(conversation):
    return is_last_message_received(conversation)
