from tests.wykop_api_test_utils import *


class TestTaktyk(object):

    def test_should_not_send_message_if_not_observed_login_add_comment(self):
        api, bot, login, repository = default_test_context()
        op_login = 'op'
        different_login = 'different'
        observer = 'observer'

        entry_id = new_entry_is_added(api, author=op_login)
        user_request_op_observation(api, entry_id, observer)

        bot.run()

        new_comment_to_entry_is_added(api, entry_id, author=different_login)

        bot.run()

        assert messages_in_conversation(api, observer) == NO_MESSAGE

    def test_should_send_message_if_observed_op_add_comment(self):
        api, bot, login, repository = default_test_context()
        op_login = 'op'
        observer = 'observer'

        entry_id = new_entry_is_added(api, author=op_login)
        user_request_op_observation(api, entry_id, observer)

        bot.run()

        new_comment_to_entry_is_added(api, entry_id, author=op_login)

        bot.run()

        assert messages_in_conversation(api, observer) == OBSERVATION_MESSAGE

    def test_should_send_correct_messages_to_different_observation_modes(self):
        api, bot, login, repository = default_test_context()
        op_login = 'op'
        observer = 'observer'
        different_observer = 'different_observer'
        different_login = 'different'

        entry_id = new_entry_is_added(api, author=op_login)
        user_request_op_observation(api, entry_id, observer)
        user_request_observation(api, entry_id, different_observer)

        bot.run()

        new_comment_to_entry_is_added(api, entry_id, author=op_login)
        bot.run()

        new_comment_to_entry_is_added(api, entry_id, author=different_login)
        bot.run()

        assert messages_in_conversation(api, observer) == OBSERVATION_MESSAGE
        assert messages_in_conversation(api, different_observer) == 2 * OBSERVATION_MESSAGE

    def test_should_not_send_messages_if_op_post_comment_before_observation_request(self):
        api, bot, login, repository = default_test_context()
        op_login = 'op'
        observer = 'observer'

        entry_id = new_entry_is_added(api, author=op_login)
        new_comment_to_entry_is_added(api, entry_id, author=op_login)

        user_request_op_observation(api, entry_id, observer)

        bot.run()

        assert messages_in_conversation(api, observer) == NO_MESSAGE

    def test_should_not_send_messages_if_last_comment_contains_observer_mention(self):
        api, bot, login, repository = default_test_context()
        observer = 'observer'
        comment_message_with_observer_mention = f'@{observer} text'

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, observer)
        bot.run()

        new_comment_to_entry_is_added(api, entry_id, body=comment_message_with_observer_mention)

        bot.run()

        assert messages_in_conversation(api, observer) == NO_MESSAGE

    def test_should_send_messages_if_after_comment_contains_observer_mention_next_comment_is_added(self):
        api, bot, login, repository = default_test_context()
        observer = 'observer'
        comment_message_with_observer_mention = f'@{observer} text'

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, observer)
        bot.run()

        new_comment_to_entry_is_added(api, entry_id, body=comment_message_with_observer_mention)
        new_comment_to_entry_is_added(api, entry_id)

        bot.run()

        assert messages_in_conversation(api, observer) == OBSERVATION_MESSAGE

    def test_not_should_send_messages_if_comment_contains_only_observation_request(self):
        api, bot, login, repository = default_test_context()
        different_login = 'different_login'

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)
        bot.run()

        user_request_observation(api, entry_id, different_login)

        bot.run()

        assert messages_in_conversation(api, login) == NO_MESSAGE

    def test_should_send_messages_if_comment_contains_only_observation_request_and_there_is_normal_comment(self):
        api, bot, login, repository = default_test_context()
        different_login = 'different_login'

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)
        bot.run()

        new_comment_to_entry_is_added(api, entry_id, different_login)
        user_request_observation(api, entry_id, different_login)

        bot.run()

        assert messages_in_conversation(api, login) == OBSERVATION_MESSAGE
