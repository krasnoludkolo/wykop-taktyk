from wykop import WykopAPI

from taktyk.message_sender import MessageSender
from taktyk.observation_repository import ObservationRepository
from taktyk.observation_saver import ObservationSaver
from taktyk.observations_remover import ObservationsRemover
from taktyk.observations_sender import ObservationsSender


class TaktykBot:

    def __init__(self, api: WykopAPI, repo: ObservationRepository):
        self.api: WykopAPI = api
        self.repo: ObservationRepository = repo
        self.observation_saver = ObservationSaver(api, repo)
        self.message_sender = MessageSender(api)
        self.observations_remover = ObservationsRemover(api, repo, self.message_sender)
        self.observations_sender = ObservationsSender(api, repo, self.message_sender)

    def run(self):
        self.observation_saver.save_new_observations()
        self.observations_remover.remove_observations_from_messages()
        self.observations_sender.send_observations()
