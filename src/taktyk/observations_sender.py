from typing import List, NoReturn

from wykop import WykopAPI
from wykop.api.exceptions import EntryDoesNotExistError

from taktyk.base_logger import logger
from taktyk.model import Observation, LoginObservation, ObservationMode
from taktyk.observation_repository import ObservationRepository
from taktyk.wykop_api_utils import comment_count_from_entry, \
    op_from_entry, comment_infos_from_entry


class EntryInfo:

    def __init__(self, entry) -> None:
        self.current_comments_count: int = comment_count_from_entry(entry)
        self.op: str = op_from_entry(entry)
        self.comments: List[CommentInfo] = [CommentInfo(comment_id, author, body)
                                            for comment_id, author, body
                                            in comment_infos_from_entry(entry)]


class CommentInfo:

    def __init__(self, comment_id: str, author: str, body: str) -> None:
        self.comment_id: str = comment_id
        self.author: str = author
        self.body: str = body


class ObservationsSender:

    def __init__(self, api: WykopAPI, repo: ObservationRepository, message_sender):
        self.api: WykopAPI = api
        self.repo: ObservationRepository = repo
        self.message_sender = message_sender

    def send_observations(self) -> None:
        active_observations = self.repo.get_all_actives()
        logger.debug(f'Found {len(active_observations)} active entry observations')
        for observation in active_observations:
            self.process_observation(observation)

    def process_observation(self, observation) -> NoReturn:
        entry_id = observation.entry_id
        logger.debug(f'Processing entry with id: {entry_id}')
        try:
            entry = self.api.entry(entry_id)
        except EntryDoesNotExistError:
            logger.info(f'Entry with id: {entry_id} no longer exists. Marking observation as inactive')
            self.repo.mark_as_inactive(entry_id)
            return
        entry_info = EntryInfo(entry)

        if observation.comments_count < entry_info.current_comments_count:
            logger.debug(f'New comments to entry with id: {entry_id}')
            logins = filter_logins_to_send_message(observation, entry_info)
            logger.debug(f'Logins to send message: {logins}')
            last_comment_id = entry_info.comments[-1].comment_id
            self.__send_message_to_logins_about_entity(last_comment_id, observation, logins)
            self.repo.set_observation_comment_count(observation.entry_id, entry_info.current_comments_count)
        else:
            logger.debug(f'No new comments to entry with id: {entry_id}')

    def __send_message_to_logins_about_entity(self, last_comment_id: str, observation: Observation,
                                              logins: List[str]) -> None:
        entry_id = observation.entry_id
        for login in logins:
            last_seen_comment_id = observation.login_observations[login].last_seen_comment_id
            self.message_sender.send_new_comment_message(last_seen_comment_id, login, entry_id)
            self.repo.set_last_seen_id_for_login(entry_id, login, last_comment_id)


def filter_logins_to_send_message(observation: Observation, entry_info: EntryInfo) -> List[str]:
    logins = observation.login_observations.values()
    return [
        login_observation.login
        for login_observation
        in logins
        if should_send_message_to_login(login_observation, entry_info)
    ]


def should_send_message_to_login(login_observation: LoginObservation, entry_info: EntryInfo) -> bool:
    if login_observation.observation_mode == ObservationMode.ALL:
        return should_send_message_with_all_observation_mode(entry_info, login_observation)
    if login_observation.observation_mode == ObservationMode.OP:
        return should_send_message_with_op_observation_mode(entry_info, login_observation)
    raise Exception('Unknown ObservationMode')


def should_send_message_with_all_observation_mode(entry_info: EntryInfo, login_observation: LoginObservation):
    login = login_observation.login
    if login_is_author_of_last_comment(login, entry_info):
        logger.debug(f'Should not send message to {login} because it\'s author of last comment')
        return False
    if login_is_mentioned_in_last_comment(login, entry_info):
        logger.debug(f'Should not send message to {login} because it\'s mentioned in last comment')
        return False
    if new_messages_are_only_observation_requests(login_observation, entry_info):
        logger.debug(f'Should not send message to {login} because new messages are observation requests')
        return False
    logger.debug(f'Should send message to {login}')
    return True


def login_is_author_of_last_comment(login: str, entry_info: EntryInfo) -> bool:
    return login == entry_info.comments[-1].author


def login_is_mentioned_in_last_comment(login: str, entry_info: EntryInfo) -> bool:
    return f'@{login}' in entry_info.comments[-1].body


def should_send_message_with_op_observation_mode(entry_info: EntryInfo, login_observation: LoginObservation) -> bool:
    comment_id = login_observation.last_seen_comment_id
    op_comment_ids = get_op_comment_ids(entry_info)
    if not op_comment_ids:
        return False
    last_op_comment_id = max(op_comment_ids)
    return str(comment_id) < str(last_op_comment_id)


def get_op_comment_ids(entry_info: EntryInfo) -> List[str]:
    return [comment.comment_id
            for comment
            in entry_info.comments
            if comment.author == entry_info.op]


def new_messages_are_only_observation_requests(login_observation: LoginObservation, entry_info: EntryInfo) -> bool:
    new_comments = [c for c in entry_info.comments if str(c.comment_id) > str(login_observation.last_seen_comment_id)]
    for comment in new_comments:
        if bot_is_not_mentioned(comment.body) or comment_is_to_long(comment.body):
            return False
    return True


def bot_is_not_mentioned(comment_body: str) -> bool:
    return BOT_MENTION not in comment_body.lower()


def comment_is_to_long(comment_body: str):
    return len(comment_body) > len(BOT_MENTION) + COMMENT_THRESHOLD


BOT_MENTION = '@taktyk-bot'
COMMENT_THRESHOLD = 4
