import logging
from typing import Tuple, List, NoReturn

from wykop import WykopAPI
from wykop.api.exceptions import EntryDoesNotExistError

from taktyk.model import Observation, LoginObservation, ObservationMode
from taktyk.observation_repository import ObservationRepository
from taktyk.wykop_api_utils import comment_count_from_entry, last_comment_id_from_entry, last_author_login_from_entry, \
    comment_authors_with_comment_id_from_entry, op_from_entry


class EntryInfo:

    def __init__(self, entry) -> None:
        self.current_comments_count: int = comment_count_from_entry(entry)
        self.last_comment_id: str = last_comment_id_from_entry(entry)
        self.last_author_login: str = last_author_login_from_entry(entry)
        self.comment_authors_with_comment_id: List[Tuple[str, str]] = comment_authors_with_comment_id_from_entry(entry)
        self.op: str = op_from_entry(entry)


class ObservationsSender:

    def __init__(self, api: WykopAPI, repo: ObservationRepository, message_sender):
        self.api: WykopAPI = api
        self.repo: ObservationRepository = repo
        self.message_sender = message_sender

    def send_observations(self) -> None:
        for observation in self.repo.get_all_actives():
            self.process_observation(observation)

    def process_observation(self, observation) -> NoReturn:
        entry_id = observation.entry_id
        try:
            entry = self.api.entry(entry_id)
        except EntryDoesNotExistError:
            logging.info(f'Entry with id: {entry_id} no longer exists. Marking observation as inactive')
            self.repo.mark_as_inactive(entry_id)
            return
        entry_info = EntryInfo(entry)

        if observation.comments_count < entry_info.current_comments_count:
            logins = filter_logins_to_send_message(observation, entry_info)
            self.__send_message_to_logins_about_entity(entry_info.last_comment_id, observation, logins)
            self.repo.set_observation_comment_count(observation.entry_id, entry_info.current_comments_count)

    def __send_message_to_logins_about_entity(self, last_comment_id: str, observation: Observation,
                                              logins: List[str]) -> None:
        entry_id = observation.entry_id
        for login in logins:
            last_seen_comment_id = observation.login_observations[login].last_seen_comment_id
            self.message_sender.send_new_comment_message(last_seen_comment_id, login, entry_id)
            self.repo.set_last_seen_id_for_login(entry_id, login, last_comment_id)


def filter_logins_to_send_message(observation: Observation, entry_info) -> List[str]:
    logins = observation.login_observations.values()
    return [
        login_observation.login
        for login_observation
        in logins
        if should_send_message_to_login(login_observation, entry_info)
    ]


def should_send_message_to_login(login_observation: LoginObservation, entry_info: EntryInfo) -> bool:
    if login_observation.login == entry_info.last_author_login:
        return False
    if login_observation.observation_mode == ObservationMode.OP:
        return should_send_message_with_op_observation_mode(entry_info, login_observation)
    return True


def should_send_message_with_op_observation_mode(entry_info, login_observation):
    comment_id = login_observation.last_seen_comment_id
    op_comment_ids = get_op_comment_ids(entry_info)
    if not op_comment_ids:
        return False
    last_op_comment_id = max(op_comment_ids)
    return str(comment_id) < str(last_op_comment_id)


def get_op_comment_ids(entry_info):
    return [comment_id
            for author, comment_id
            in entry_info.comment_authors_with_comment_id
            if author == entry_info.op]
