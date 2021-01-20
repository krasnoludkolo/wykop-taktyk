from typing import List
from wykop import WykopAPI, WykopAPIError

import logging

from taktyk.reminder_repository import ReminderRepository
from taktyk.model import Reminder, entry_url


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
                login = n['author']['login']
                comment_id = n['subitem_id']
                reminder = Reminder({login: comment_id}, n['item_id'], comment_id, entry['comments_count'])
                result.append(reminder)
        return result

    def save_new_reminders(self):
        for nicks_with_last_seen_comment_id, entry_id, comment_id, comments_count in self.new_reminders():
            if self.repo.has_entry(entry_id):
                self.repo.add_nick_to_remainder(entry_id, nicks_with_last_seen_comment_id)
                saved_comments_count = self.repo.get_comment_count(entry_id)
                self.repo.set_reminder_comment_count(entry_id, max(saved_comments_count, comments_count))
                logging.info(f'reminder update: {entry_id} {max(saved_comments_count, comments_count)}')
            else:
                reminder = Reminder(nicks_with_last_seen_comment_id, entry_id, comment_id, comments_count)
                logging.info(f'new reminder: {reminder}')
                self.repo.save(reminder)
        self.api.notification_mark_all_as_read()

    def send_reminders(self):
        for reminder in self.repo.get_all():
            entry = self.api.entry(reminder.entry_id)
            current_comments_count = entry['comments_count']
            last_comment_id = entry['comments'][-1]['id']
            if reminder.comments_count < current_comments_count:
                for nick, last_seen_comment_id in reminder.nicks_with_last_seen_comment_id.items():
                    logging.info(f'send to {nick}')
                    try:
                        message = f'nowy komentarz {entry_url}/{reminder.entry_id}#comment-{last_seen_comment_id}'
                        self.api.message_send(nick, message)
                        self.repo.set_last_seen_id_for_nick(reminder.entry_id, nick, last_comment_id)
                    except WykopAPIError:
                        logging.info(f'Error during sending message to {nick}')
                self.repo.set_reminder_comment_count(reminder.entry_id, current_comments_count)
