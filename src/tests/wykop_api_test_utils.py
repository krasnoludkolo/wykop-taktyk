from random import randint
from typing import Tuple

from wykop import WykopAPI

from taktyk.observation_repository import InMemoryObservationRepository
from taktyk.taktyk_bot import TaktykBot
from tests.FakeWykopApi import FakeWykopApi


def new_entry_is_added(api, start_comments_count=0) -> str:
    entry_id = str(randint(100000, 900000))
    api.add_entry(entry_id, start_comments_count)
    return entry_id


def entry_is_removed(api: WykopAPI, entry_id):
    api.entry_delete(entry_id)


def user_request_observation(api: FakeWykopApi, entry_id, login, page=1):
    api.add_comment_to_entry(entry_id)
    api.add_notification(login, entry_id, 'sub-id-1', page)


def user_send_message(api, login, message):
    api.receive_message(login, message)


def new_comments_to_entry_are_added(api: FakeWykopApi, entry_id, author='test_login'):
    api.add_comment_to_entry(entry_id, author)


def messages_with(api, login):
    return [m['body'] for m in api.conversation(login)]


def default_test_context() -> Tuple[FakeWykopApi, TaktykBot, str, InMemoryObservationRepository]:
    login = 'login1'
    repository = InMemoryObservationRepository()
    api = FakeWykopApi()
    bot = TaktykBot(api, repository)
    return api, bot, login, repository


USER_MESSAGE = 1
REMOVED_SUMMARY_MESSAGE = 1
NOTHING_TO_REMOVE_MESSAGE = 1
USER_OBSERVATION_REQUEST = 1
