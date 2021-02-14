from tests.wykop_api_test_utils import *


class TestTaktykReceiveMessages(object):

    def test_do_not_send_message_if_user_remove_observation_by_sending_link(self):
        api, bot, login, _ = default_test_context()

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)
        bot.run()

        user_send_message(api, login, f'https://www.wykop.pl/wpis/{entry_id}')
        new_comment_to_entry_is_added(api, entry_id)
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + REMOVED_SUMMARY_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message

    def test_do_not_send_message_if_user_remove_observation_by_sending_link_with_comment_id(self):
        api, bot, login, _ = default_test_context()

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)
        bot.run()

        user_send_message(api, login, f'https://www.wykop.pl/wpis/{entry_id}#comment-195807281')
        new_comment_to_entry_is_added(api, entry_id)
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + REMOVED_SUMMARY_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message

    def test_do_not_send_message_if_user_remove_observation_by_sending_entry_id(self):
        api, bot, login, _ = default_test_context()

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)
        bot.run()

        user_send_message(api, login, f'{entry_id}')
        new_comment_to_entry_is_added(api, entry_id)
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + REMOVED_SUMMARY_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message

    def test_do_not_send_message_if_user_remove_more_then_one_observation(self):
        api, bot, login, _ = default_test_context()

        entry_id1 = new_entry_is_added(api)
        entry_id2 = new_entry_is_added(api)
        user_request_observation(api, entry_id1, login)
        user_request_observation(api, entry_id2, login)
        bot.run()

        user_send_message(api, login, f'{entry_id1}')
        user_send_message(api, login, f'{entry_id2}')
        new_comment_to_entry_is_added(api, entry_id1)
        new_comment_to_entry_is_added(api, entry_id2)
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + USER_MESSAGE + REMOVED_SUMMARY_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message

    def test_should_ignore_removing_non_existing_observation(self):
        api, bot, login, _ = default_test_context()

        user_send_message(api, login, f'1000')
        bot.run()

        assert len(api.conversation(login)) == USER_MESSAGE + NOTHING_TO_REMOVE_MESSAGE
        for message in messages_with(api, login):
            assert 'nowy komentarz' not in message
