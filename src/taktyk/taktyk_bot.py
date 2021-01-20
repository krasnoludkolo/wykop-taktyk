from typing import List
from wykop import WykopAPI, WykopAPIError

import logging

from taktyk.reminder_repository import ReminderRepository
from taktyk.model import Reminder, ReminderCandidate, entry_url


def all_new(notifications):
    if len(notifications) == 0:
        return False
    for notification in notifications:
        if not notification['new']:
            return False
    return True


class TaktykBot:

    def __init__(self, api: WykopAPI, repo: ReminderRepository):
        self.api: WykopAPI = api
        self.repo: ReminderRepository = repo

    def __new_notifications(self, page=1) -> List:
        api = self.api
        notifications = [x for x in api.notifications_direct(page) if x['type'] == 'entry_comment_directed']
        result = []
        if all_new(notifications):
            result += self.__new_notifications(page + 1)
        result += notifications
        return result

    def new_reminders(self) -> List[ReminderCandidate]:
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
        for login, entry_id, comment_id, comments_count in self.new_reminders():
            if self.repo.has_entry(entry_id):
                self.update_login_reminder(comments_count, entry_id, {login: comment_id})
            else:
                self.save_new_reminder(comment_id, comments_count, entry_id, {login: comment_id})
        self.api.notification_mark_all_as_read()

    def update_login_reminder(self, comments_count, entry_id, logins_with_last_seen_comment_id):
        self.repo.add_login_to_remainder(entry_id, logins_with_last_seen_comment_id)
        saved_comments_count = self.repo.get_comment_count(entry_id)
        self.repo.set_reminder_comment_count(entry_id, max(saved_comments_count, comments_count))
        logging.info(f'reminder update: {entry_id} {max(saved_comments_count, comments_count)}')

    def save_new_reminder(self, comment_id, comments_count, entry_id, logins_with_last_seen_comment_id):
        reminder = Reminder(logins_with_last_seen_comment_id, entry_id, comment_id, comments_count)
        logging.info(f'new reminder: {reminder}')
        self.repo.save(reminder)

    def send_reminders(self):
        for reminder in self.repo.get_all():
            current_comments_count, last_comment_id = self.get_entry_comments_info(reminder)
            if reminder.comments_count < current_comments_count:
                self.send_message_to_all_logins(current_comments_count, last_comment_id, reminder)

    def get_entry_comments_info(self, reminder):
        entry = self.api.entry(reminder.entry_id)
        current_comments_count = entry['comments_count']
        last_comment_id = entry['comments'][-1]['id']
        return current_comments_count, last_comment_id

    def send_message_to_all_logins(self, current_comments_count, last_comment_id, reminder):
        for login, last_seen_comment_id in reminder.logins_with_last_seen_comment_id.items():
            self.send_message_to_login(last_comment_id, last_seen_comment_id, login, reminder)
        self.repo.set_reminder_comment_count(reminder.entry_id, current_comments_count)

    def send_message_to_login(self, last_comment_id, last_seen_comment_id, login, reminder):
        logging.info(f'send to {login}')
        try:
            message = f'nowy komentarz {entry_url}/{reminder.entry_id}#comment-{last_seen_comment_id}'
            self.api.message_send(login, message)
            self.repo.set_last_seen_id_for_login(reminder.entry_id, login, last_comment_id)
        except WykopAPIError:
            logging.info(f'Error during sending message to {login}')
