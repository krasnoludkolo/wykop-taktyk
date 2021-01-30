import logging
import re
from typing import Optional

from wykop import WykopAPI

from taktyk.message_sender import MessageSender
from taktyk.observation_repository import ObservationRepository
from taktyk.wykop_api_utils import *


class ObservationsRemover:
    def __init__(self, api: WykopAPI, repo: ObservationRepository, message_sender: MessageSender):
        self.api: WykopAPI = api
        self.repo: ObservationRepository = repo
        self.message_sender = message_sender
        self.url_entry_id_pattern = re.compile(r'wpis/\d+')

    def remove_observations_from_messages(self):
        for conversation_summary in self.api.conversations_list():
            self.__process_conversation(conversation_summary)

    def __process_conversation(self, conversation_summary):
        login = get_login_from_conversation_summary(conversation_summary)
        conversation = self.api.conversation(login)
        if has_new_messages(conversation):
            self.__parse_messages(conversation, login)

    def __parse_messages(self, conversation: Conversation, login: str):
        new_messages = take_new_messages(conversation)
        entry_ids_from_removed_observations = []
        for message in take_messages_body(new_messages):
            removed_id = self.__remove_observation_from_message(login, message)
            if removed_id:
                entry_ids_from_removed_observations += removed_id
        self.__send_summary_to_login(entry_ids_from_removed_observations, login)

    def __remove_observation_from_message(self, login, message) -> Optional[str]:
        entry_id = self.__take_entry_id_from_message(message)
        if self.repo.has_observation_with_login(entry_id, login):
            logging.info(f'Removing {login} from {entry_id}')
            self.repo.remove_login_from_observation(entry_id, login)
            return entry_id
        return None

    def __send_summary_to_login(self, entry_ids_from_removed_observations, login):
        if entry_ids_from_removed_observations:
            self.message_sender.send_removed_observation_message(login, entry_ids_from_removed_observations)
        else:
            self.message_sender.send_no_observation_to_remove_message(login)

    def __take_entry_id_from_message(self, message: str) -> str:
        if message.isdigit():
            return message
        else:
            return str(self.url_entry_id_pattern.findall(message)[0]).split('/')[1]


def has_new_messages(conversation):
    return is_last_message_received(conversation)
