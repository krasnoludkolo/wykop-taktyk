import logging
import re

from wykop import WykopAPI

from taktyk.message_sender import MessageSender
from taktyk.reminder_repository import ReminderRepository
from taktyk.saver import ReminderSaver
from taktyk.wykop_api_utils import *


class TaktykBot:

    def __init__(self, api: WykopAPI, repo: ReminderRepository):
        self.api: WykopAPI = api
        self.repo: ReminderRepository = repo
        self.url_entry_id_pattern = re.compile('wpis\/\d+')
        self.reminder_saver = ReminderSaver(api, repo)
        self.message_sender = MessageSender(api)

    def run(self):
        self.reminder_saver.save_new_reminders()
        self.remove_reminders_from_messages()
        self.send_reminders()

    def send_reminders(self):
        for reminder in self.repo.get_all():
            current_comments_count, last_comment_id = self.__get_entry_comments_info(reminder)
            if reminder.comments_count < current_comments_count:
                self.__send_message_to_all_logins(current_comments_count, last_comment_id, reminder)

    def __get_entry_comments_info(self, reminder):
        entry = self.api.entry(reminder.entry_id)
        current_comments_count = entry['comments_count']
        last_comment_id = entry['comments'][-1]['id']
        return current_comments_count, last_comment_id

    def __send_message_to_all_logins(self, current_comments_count, last_comment_id, reminder):
        for login, last_seen_comment_id in reminder.logins_with_last_seen_comment_id.items():
            self.message_sender.send_reminder_to_login(last_seen_comment_id, login, reminder)
            self.repo.set_last_seen_id_for_login(reminder.entry_id, login, last_comment_id)
        self.repo.set_reminder_comment_count(reminder.entry_id, current_comments_count)

    def remove_reminders_from_messages(self):
        for conversation_summary in self.api.conversations_list():
            login = get_login_from_conversation_summary(conversation_summary)
            conversation = self.api.conversation(login)
            if is_last_message_received(conversation):
                messages = take_last_received_messages(conversation)
                entry_ids_from_removed_reminders = []
                for message in take_messages_body(messages):
                    entry_id = self.__take_entry_id_from_message(message)
                    if self.repo.has_reminder_with_login(entry_id, login):
                        logging.info(f'Removing {login} from {entry_id}')
                        self.repo.remove_login_from_reminder(entry_id, login)
                        entry_ids_from_removed_reminders.append(entry_id)
                if entry_ids_from_removed_reminders:
                    self.message_sender.send_removed_reminder_message(login, entry_ids_from_removed_reminders)
                else:
                    self.message_sender.send_no_reminder_to_remove_message(login)

        pass

    def __take_entry_id_from_message(self, message: str) -> str:
        if message.isdigit():
            return message
        else:
            return str(self.url_entry_id_pattern.findall(message)[0]).split('/')[1]
