from typing import Dict, List, Any

from wykop import WykopAPI
from wykop.api.exceptions import EntryDoesNotExistError

from taktyk.wykop_api_utils import Conversation


class FakeWykopApi(WykopAPI):

    def __init__(self):
        super().__init__('appkey', 'secretkey')
        self.notifications: Dict[int, list] = {}
        self.entries: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
        self.conversations_summary: Dict[str, Dict[str, Any]] = {}

    def notifications_direct(self, page=1):
        if page not in self.notifications:
            return []
        return self.notifications[page]

    def notification_mark_all_as_read(self):
        for key in self.notifications.keys():
            for n in self.notifications[key]:
                n['new'] = False

    def authenticate(self, account_key=None, login=None, password=None):
        pass

    def entry(self, entry_id):
        if entry_id in self.entries:
            return self.entries[entry_id]
        else:
            raise EntryDoesNotExistError

    def add_notification(self, login: str, item_id, subitem_id, page):
        if page not in self.notifications:
            self.notifications[page] = []
        self.notifications[page].append(notification(login, item_id, subitem_id))

    def add_entry(self, item_id, comments_count, author):
        self.entries[item_id] = new_entity(author)
        for _ in range(comments_count):
            self.add_comment_to_entry(item_id)

    def message_send(self, receiver: str, message: str):
        if receiver not in self.conversations:
            self.conversations[receiver] = []
        if receiver not in self.conversations_summary:
            self.conversations_summary[receiver] = new_conversation_summary(receiver)
        self.conversations[receiver].append(message_sent(message))

    def add_comment_to_entry(self, entry_id: str, author: str = 'test_login') -> str:
        comments_count = self.entries[entry_id]['comments_count']
        comment_id = f'sub-id-{comments_count}'
        self.entries[entry_id]['comments_count'] = comments_count + 1
        self.entries[entry_id]['comments'].append(new_comment(author, comment_id))
        return str(comment_id)

    def conversations_list(self) -> List[Dict[str, str]]:
        return list(self.conversations_summary.values())

    def conversation(self, receiver: str) -> Conversation:
        if receiver in self.conversations:
            return self.conversations[receiver]
        return []

    def receive_message(self, sender: str, message: str):
        if sender not in self.conversations:
            self.conversations[sender] = []
        if sender not in self.conversations_summary:
            self.conversations_summary[sender] = new_conversation_summary(sender)
        self.conversations[sender].append(message_received(message))

    def entry_delete(self, entry_id: str):
        self.entries.pop(entry_id)


def notification(login: str, item_id, subitem_id: str) -> Dict[str, Any]:
    return {
        'author': {'login': login},
        'item_id': item_id,
        'subitem_id': subitem_id,
        'new': True,
        'type': 'entry_comment_directed'
    }


def new_entity(author: str) -> Dict[str, Any]:
    return {
        'comments_count': 0,
        'comments': [],
        'author': {
            'login': author
        }
    }


def new_comment(author, comment_id):
    return {'id': comment_id, 'author': {'login': author}}


def new_conversation_summary(sender):
    return {'receiver': {'login': sender}}


def message_sent(body: str) -> Dict[str, str]:
    return {
        'body': body,
        'direction': 'sended'
    }


def message_received(body: str) -> Dict[str, str]:
    return {
        'body': body,
        'direction': 'received'
    }
