from random import randint

from taktyk.reminder_repository import InMemoryReminderRepository
from taktyk.taktyk_bot import TaktykBot
from tests.FakeWykopApi import FakeWykopApi


class TestTaktykReceiveMessages(object):

    def test_do_not_send_message_if_user_remove_observation_by_sending_link(self):
        api, bot, login, start_comments_count = default_test_context()

        entry_id = new_entity_is_added(api, start_comments_count)
        user_request_observation(api, entry_id, login)
        bot.run()

        user_send_message(api, login, f'https://www.wykop.pl/wpis/{entry_id}')
        new_comments_to_entity_are_added(api, entry_id, start_comments_count + 1)
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + REMOVED_SUMMARY_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message

    def test_do_not_send_message_if_user_remove_observation_by_sending_link_with_comment_id(self):
        api, bot, login, start_comments_count = default_test_context()

        entry_id = new_entity_is_added(api, start_comments_count)
        user_request_observation(api, entry_id, login)
        bot.run()

        api.receive_message(login, f'https://www.wykop.pl/wpis/{entry_id}#comment-195807281')
        new_comments_to_entity_are_added(api, entry_id, start_comments_count + 1)
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + REMOVED_SUMMARY_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message

    def test_do_not_send_message_if_user_remove_observation_by_sending_entry_id(self):
        api, bot, login, start_comments_count = default_test_context()

        entry_id = new_entity_is_added(api, start_comments_count)
        user_request_observation(api, entry_id, login)
        bot.run()

        api.receive_message(login, f'{entry_id}')
        new_comments_to_entity_are_added(api, entry_id, start_comments_count + 1)
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + REMOVED_SUMMARY_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message

    def test_do_not_send_message_if_user_remove_more_then_one_observation(self):
        api, bot, login, start_comments_count = default_test_context()

        entry_id1 = new_entity_is_added(api, start_comments_count)
        entry_id2 = new_entity_is_added(api, start_comments_count)
        user_request_observation(api, entry_id1, login)
        user_request_observation(api, entry_id2, login)
        bot.run()

        api.receive_message(login, f'{entry_id1}')
        api.receive_message(login, f'{entry_id2}')
        new_comments_to_entity_are_added(api, entry_id1, start_comments_count + 1)
        new_comments_to_entity_are_added(api, entry_id2, start_comments_count + 1)
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + USER_MESSAGE + REMOVED_SUMMARY_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message

    def test_should_ignore_removing_non_existing_observation(self):
        api, bot, login, start_comments_count = default_test_context()

        api.receive_message(login, f'1000')
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + NOTHING_TO_REMOVE_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message


def new_entity_is_added(api, start_comments_count) -> str:
    entry_id = str(randint(100000, 900000))
    api.add_entry(entry_id, start_comments_count)
    return entry_id


def user_request_observation(api, entry_id, login):
    api.add_notification(login, entry_id, 'sub-id-1', 1)


def user_send_message(api, login, message):
    api.receive_message(login, message)


def new_comments_to_entity_are_added(api, entry_id, number_of_all_comments):
    api.set_entry_comments_count(entry_id, number_of_all_comments)


def messages_with(api, login):
    return [m['body'] for m in api.conversation(login)]


def default_test_context():
    start_comments_count = 1
    login = 'login1'
    repository = InMemoryReminderRepository()
    api = FakeWykopApi()
    bot = TaktykBot(api, repository)
    return api, bot, login, start_comments_count


USER_MESSAGE = 1
REMOVED_SUMMARY_MESSAGE = 1
NOTHING_TO_REMOVE_MESSAGE = 1
