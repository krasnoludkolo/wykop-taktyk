from typing import List
from wykop import WykopAPI, WykopAPIError
import re
import logging

from taktyk.reminder_repository import ReminderRepository
from taktyk.model import Reminder, ReminderCandidate, entry_url
from taktyk.wykop_api_utils import *


class TaktykBot:

    def __init__(self, api: WykopAPI, repo: ReminderRepository):
        self.api: WykopAPI = api
        self.repo: ReminderRepository = repo
        self.url_entity_id_pattern = re.compile('wpis\/\d+')

    def run(self):
        self.save_new_reminders()
        self.remove_reminders_from_messages()
        self.send_reminders()

    def __new_notifications(self, page=1) -> List:
        api = self.api
        notifications = [x for x in api.notifications_direct(page) if x['type'] == 'entry_comment_directed']
        result = []
        if all_new(notifications):
            result += self.__new_notifications(page + 1)
        result += notifications
        return result

    def __new_reminders(self) -> List[ReminderCandidate]:
        result = []
        for n in self.__new_notifications():
            if n['new']:
                entry = self.api.entry(n['item_id'])
                login = n['author']['login']
                comment_id = n['subitem_id']
                reminder = ReminderCandidate(login, n['item_id'], comment_id, entry['comments_count'])
                result.append(reminder)
        return result

    def save_new_reminders(self):
        for login, entry_id, comment_id, comments_count in self.__new_reminders():
            if self.repo.has_entry(entry_id):
                self.__update_login_reminder(comments_count, entry_id, {login: comment_id})
            else:
                self.__save_new_reminder(comment_id, comments_count, entry_id, {login: comment_id})
        self.api.notification_mark_all_as_read()

    def __update_login_reminder(self, comments_count, entry_id, logins_with_last_seen_comment_id):
        self.repo.add_login_to_remainder(entry_id, logins_with_last_seen_comment_id)
        saved_comments_count = self.repo.get_comment_count(entry_id)
        self.repo.set_reminder_comment_count(entry_id, max(saved_comments_count, comments_count))
        logging.info(f'reminder update: {entry_id} {max(saved_comments_count, comments_count)}')

    def __save_new_reminder(self, comment_id, comments_count, entry_id, logins_with_last_seen_comment_id):
        reminder = Reminder(logins_with_last_seen_comment_id, entry_id, comment_id, comments_count)
        logging.info(f'new reminder: {reminder}')
        self.repo.save(reminder)

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
            self.__send_message_to_login(last_comment_id, last_seen_comment_id, login, reminder)
        self.repo.set_reminder_comment_count(reminder.entry_id, current_comments_count)

    def __send_message_to_login(self, last_comment_id, last_seen_comment_id, login, reminder):
        logging.info(f'send to {login}')
        try:
            message = f'nowy komentarz {entry_url}/{reminder.entry_id}#comment-{last_seen_comment_id}'
            self.api.message_send(login, message)
            self.repo.set_last_seen_id_for_login(reminder.entry_id, login, last_comment_id)
        except WykopAPIError:
            logging.info(f'Error during sending message to {login}')

    def remove_reminders_from_messages(self):
        for conversation_summary in self.api.conversations_list():
            login = get_login_from_conversation_summary(conversation_summary)
            conversation = self.api.conversation(login)
            if is_last_message_received(conversation):
                messages = take_last_received_messages(conversation)
                entity_ids_from_removed_reminders = []
                for message in take_messages_body(messages):
                    entry_id = self.__take_entry_id_from_message(message)
                    if self.repo.has_reminder_with_login(entry_id,login):
                        logging.info(f'Removing {login} from {entry_id}')
                        self.repo.remove_login_from_reminder(entry_id, login)
                        entity_ids_from_removed_reminders.append(entry_id)
                if entity_ids_from_removed_reminders:
                    self.api.message_send(login, f'Usunięto: {"".join(entity_ids_from_removed_reminders)}')
                else:
                    self.api.message_send(login, 'Nic do usunięcia')

        pass

    def __take_entry_id_from_message(self, message: str) -> str:
        if message.isdigit():
            return message
        else:
            return str(self.url_entity_id_pattern.findall(message)[0]).split('/')[1]
