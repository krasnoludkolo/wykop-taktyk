import os
from random import randint
from typing import Tuple

from wykop import WykopAPI

from taktyk.observation_repository import InMemoryObservationRepository, ObservationRepository, \
    ShelveObservationRepository
from taktyk.taktyk_bot import TaktykBot
from tests.FakeWykopApi import FakeWykopApi

TEST_DB_FILE = 'test.db'


def new_entry_is_added(api, start_comments_count=0, author='test_login') -> str:
    entry_id = str(randint(100000, 900000))
    api.add_entry(entry_id, start_comments_count, author)
    return entry_id


def entry_is_removed(api: WykopAPI, entry_id):
    api.entry_delete(entry_id)


def user_request_observation(api: FakeWykopApi, entry_id, login, page=1) -> str:
    comment_id = api.add_comment_to_entry(entry_id)
    api.add_notification(login, entry_id, comment_id, page)
    return comment_id


def user_send_message(api, login, message):
    api.receive_message(login, message)


def new_comments_to_entry_are_added(api: FakeWykopApi, entry_id, author='test_login', body='@taktyk-bot .') -> str:
    return api.add_comment_to_entry(entry_id, author, body)


def messages_with(api, login):
    return [m['body'] for m in api.conversation(login)]


def messages_in_conversation(api, login):
    return len(api.conversation(login))


def default_test_context(in_memory=True) -> Tuple[FakeWykopApi, TaktykBot, str, ObservationRepository]:
    if in_memory:
        repository = InMemoryObservationRepository()
    else:
        if os.path.isfile(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
        repository = ShelveObservationRepository(TEST_DB_FILE)
    login = 'login1'
    api = FakeWykopApi()
    bot = TaktykBot(api, repository)
    return api, bot, login, repository


NO_MESSAGE = 0
USER_MESSAGE = 1
REMOVED_SUMMARY_MESSAGE = 1
NOTHING_TO_REMOVE_MESSAGE = 1
OBSERVATION_MESSAGE = 1
USER_OBSERVATION_REQUEST = 1
