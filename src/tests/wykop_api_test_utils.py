from random import randint
from typing import Tuple

from taktyk.reminder_repository import InMemoryReminderRepository, ReminderRepository
from taktyk.taktyk_bot import TaktykBot
from tests.FakeWykopApi import FakeWykopApi


def new_entry_is_added(api, start_comments_count) -> str:
    entry_id = str(randint(100000, 900000))
    api.add_entry(entry_id, start_comments_count)
    return entry_id


def user_request_observation(api, entry_id, login):
    api.add_notification(login, entry_id, 'sub-id-1', 1)


def user_send_message(api, login, message):
    api.receive_message(login, message)


def new_comments_to_entry_are_added(api, entry_id, number_of_all_comments):
    api.set_entry_comments_count(entry_id, number_of_all_comments)


def messages_with(api, login):
    return [m['body'] for m in api.conversation(login)]


def default_test_context() -> Tuple[FakeWykopApi, TaktykBot, str, ReminderRepository, int]:
    start_comments_count = 1
    login = 'login1'
    repository = InMemoryReminderRepository()
    api = FakeWykopApi()
    bot = TaktykBot(api, repository)
    return api, bot, login, repository, start_comments_count


USER_MESSAGE = 1
REMOVED_SUMMARY_MESSAGE = 1
NOTHING_TO_REMOVE_MESSAGE = 1
