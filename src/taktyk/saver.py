import logging
from typing import List

from wykop import WykopAPI

from taktyk.model import ReminderCandidate, Reminder
from taktyk.reminder_repository import ReminderRepository
from taktyk.wykop_api_utils import all_new, is_notification_new, reminder_data_from_notification, \
    comment_count_from_entry, is_notification_comment_directed


class ReminderSaver:

    def __init__(self, api: WykopAPI, repo: ReminderRepository):
        self.api: WykopAPI = api
        self.repo: ReminderRepository = repo

    def save_new_reminders(self):
        for login, entry_id, comment_id, comments_count in self.__new_reminders():
            if self.repo.has_entry(entry_id):
                self.__update_login_reminder(comments_count, entry_id, {login: comment_id})
            else:
                self.__save_new_reminder(comment_id, comments_count, entry_id, {login: comment_id})
        self.api.notification_mark_all_as_read()

    def __new_reminders(self) -> List[ReminderCandidate]:
        result = []
        for n in self.__new_notifications():
            entry_id, login, comment_id = reminder_data_from_notification(n)
            entry = self.api.entry(entry_id)
            comments_count = comment_count_from_entry(entry)
            reminder = ReminderCandidate(login, entry_id, comment_id, comments_count)
            result.append(reminder)
        return result

    def __new_notifications(self, page=1) -> List:
        notifications = [n for n in self.api.notifications_direct(page) if is_notification_comment_directed(n)]
        result = []
        if all_new(notifications):
            result += self.__load_next_page(page)
        result += notifications
        return [n for n in result if is_notification_new(n)]

    def __load_next_page(self, page):
        return self.__new_notifications(page + 1)

    def __update_login_reminder(self, comments_count, entry_id, login_with_last_seen_comment_id):
        self.repo.add_login_to_remainder(entry_id, login_with_last_seen_comment_id)
        saved_comments_count = self.repo.get_comment_count(entry_id)
        self.repo.set_reminder_comment_count(entry_id, max(saved_comments_count, comments_count))
        logging.info(f'reminder update: {entry_id} {max(saved_comments_count, comments_count)}')

    def __save_new_reminder(self, comment_id, comments_count, entry_id, login_with_last_seen_comment_id):
        reminder = Reminder(login_with_last_seen_comment_id, entry_id, comment_id, comments_count)
        self.repo.save(reminder)
        logging.info(f'new reminder: {reminder}')
