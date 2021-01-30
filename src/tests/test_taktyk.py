from tests.wykop_api_test_utils import *


class TestTaktyk(object):

    def test_get_observations_from_more_then_one_page(self):
        repository = InMemoryObservationRepository()
        api = FakeWykopApi()
        api.add_notification('login1', 'id-1', 'sub-id-1', 1)
        api.add_notification('login3', 'id-2', 'sub-id-1', 1)
        api.add_notification('login4', 'id-3', 'sub-id-1', 2)
        api.add_notification('login5', 'id-4', 'sub-id-1', 2)
        api.add_entry('id-1', 1)
        api.add_entry('id-2', 1)
        api.add_entry('id-3', 1)
        api.add_entry('id-4', 1)

        bot = TaktykBot(api, repository)
        bot.run()

        assert len(repository.observations) == 4

    def test_get_observations_from_more_then_one_user_to_one_entry(self):
        repository = InMemoryObservationRepository()
        api = FakeWykopApi()
        entry_id = 'id-1'
        api.add_notification('login1', entry_id, 'sub-id-1', 1)
        api.add_notification('login3', entry_id, 'sub-id-1', 1)
        api.add_entry(entry_id, 2)

        bot = TaktykBot(api, repository)
        bot.run()

        assert len(repository.observations) == 1
        assert len(list(repository.observations.values())[0].logins_with_last_seen_comment_id) == 2
        assert list(repository.observations.values())[0].comments_count == 2

    def test_should_not_take_read_notification_again(self):
        api, bot, login, repository, start_comments_count = default_test_context()

        entry_id = new_entry_is_added(api, start_comments_count)
        api.add_notification('login1', entry_id, 'sub-id-1', 1)

        bot.run()
        bot.run()

        assert len(list(repository.observations.values())) == 1
