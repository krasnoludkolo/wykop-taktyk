from typing import Dict, List

from wykop import WykopAPI

from ReminderRepository import ReminderRepository
from model import Reminder


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

    def new_reminders(self) -> List[Reminder]:
        result = []
        for n in self.__new_notifications():
            if n['new']:
                entry = self.api.entry(n['item_id'])
                reminder = Reminder(n['author']['login'], n['item_id'], n['subitem_id'], entry['comments_count'])
                result.append(reminder)
        return result

    def save_new_reminders(self):
        for nick, entry_id, comment_id, comments_count in self.new_reminders():
            reminder = Reminder(nick, entry_id, comment_id, comments_count)
            self.repo.save(reminder)
        self.api.notification_mark_all_as_read()
