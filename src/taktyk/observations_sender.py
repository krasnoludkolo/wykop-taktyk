import logging
from typing import Tuple

from wykop import WykopAPI
from wykop.api.exceptions import EntryDoesNotExistError

from taktyk.observation_repository import ObservationRepository
from taktyk.wykop_api_utils import comment_count_from_entry, last_comment_id_from_entry, last_author_login_from_entry


def get_entry_comments_info(entry) -> Tuple[int, str, str]:
    current_comments_count = comment_count_from_entry(entry)
    last_comment_id = last_comment_id_from_entry(entry)
    last_author_login = last_author_login_from_entry(entry)
    return current_comments_count, last_comment_id, last_author_login


class ObservationsSender:

    def __init__(self, api: WykopAPI, repo: ObservationRepository, message_sender):
        self.api: WykopAPI = api
        self.repo: ObservationRepository = repo
        self.message_sender = message_sender

    def send_observations(self) -> None:
        for observation in self.repo.get_all_actives():
            entry_id = observation.entry_id
            try:
                entry = self.api.entry(entry_id)
            except EntryDoesNotExistError:
                logging.info(f'Entry with id: {entry_id} no longer exists. Marking observation as inactive')
                self.repo.mark_as_inactive(entry_id)
                continue
            current_comments_count, last_comment_id, last_author_login = get_entry_comments_info(entry)

            if observation.comments_count < current_comments_count:
                self.__send_message_to_all_logins_about_entity(last_comment_id, observation, last_author_login)
                self.repo.set_observation_comment_count(observation.entry_id, current_comments_count)

    def __send_message_to_all_logins_about_entity(self, last_comment_id, observation, last_author_login) -> None:
        for login, last_seen_comment_id in observation.logins_with_last_seen_comment_id.items():
            entry_id = observation.entry_id
            if login != last_author_login:
                self.message_sender.send_new_comment_message(last_seen_comment_id, login, entry_id)
            self.repo.set_last_seen_id_for_login(entry_id, login, last_comment_id)
