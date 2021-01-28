from wykop import WykopAPI
from wykop.api.exceptions import EntryDoesNotExistError

from taktyk.reminder_repository import ReminderRepository
from taktyk.wykop_api_utils import comment_count_from_entry, last_comment_id_from_entry


def get_entry_comments_info(entry):
    current_comments_count = comment_count_from_entry(entry)
    last_comment_id = last_comment_id_from_entry(entry)
    return current_comments_count, last_comment_id


class RemindersSender:

    def __init__(self, api: WykopAPI, repo: ReminderRepository, message_sender):
        self.api: WykopAPI = api
        self.repo: ReminderRepository = repo
        self.message_sender = message_sender

    def send_reminders(self):
        for reminder in self.repo.get_all():
            entry_id = reminder.entry_id
            # TODO https://github.com/krasnoludkolo/wykop-taktyk/issues/26
            try:
                entry = self.api.entry(entry_id)
            except EntryDoesNotExistError:
                continue
            current_comments_count, last_comment_id = get_entry_comments_info(entry)
            if reminder.comments_count < current_comments_count:
                self.__send_message_to_all_logins(current_comments_count, last_comment_id, reminder)

    def __send_message_to_all_logins(self, current_comments_count, last_comment_id, reminder):
        for login, last_seen_comment_id in reminder.logins_with_last_seen_comment_id.items():
            self.message_sender.send_reminder_to_login(last_seen_comment_id, login, reminder)
            self.repo.set_last_seen_id_for_login(reminder.entry_id, login, last_comment_id)
        self.repo.set_reminder_comment_count(reminder.entry_id, current_comments_count)
