from wykop import WykopAPI

from taktyk.message_sender import MessageSender
from taktyk.reminder_repository import ReminderRepository
from taktyk.reminders_remover import RemindersRemover
from taktyk.saver import ReminderSaver


class TaktykBot:

    def __init__(self, api: WykopAPI, repo: ReminderRepository):
        self.api: WykopAPI = api
        self.repo: ReminderRepository = repo
        self.reminder_saver = ReminderSaver(api, repo)
        self.message_sender = MessageSender(api)
        self.reminders_remover = RemindersRemover(api, repo, self.message_sender)

    def run(self):
        self.reminder_saver.save_new_reminders()
        self.reminders_remover.remove_reminders_from_messages()
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

