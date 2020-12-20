from typing import List
from wykop import WykopAPI

from ReminderRepository import ReminderRepository
from model import Reminder, entry_url


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
            if self.repo.has_entry(entry_id):
                self.repo.add_nick_to_remainder(entry_id, nick)
                saved_comments_count = self.repo.get_comment_count(entry_id)
                self.repo.set_reminder_comment_count(entry_id, max(saved_comments_count, comments_count))
                print(f'reminder update: {entry_id} {max(saved_comments_count, comments_count)}')
            else:
                reminder = Reminder(nick, entry_id, comment_id, comments_count)
                print(f'new reminder: {reminder}')
                self.repo.save(reminder)
        self.api.notification_mark_all_as_read()

    def send_reminders(self):
        for reminder in self.repo.get_all():
            current_comments_count = self.api.entry(reminder.entry_id)['comments_count']
            if reminder.comments_count < current_comments_count:
                for nick in reminder.nicks:
                    # TODO aggregate messages to one user
                    print(f'send to {nick}')
                    # TODO navigate to first unread?
                    self.api.send_message(nick, f'nowy komentarz w {entry_url}/{reminder.entry_id}')
                self.repo.set_reminder_comment_count(reminder.entry_id, current_comments_count)
