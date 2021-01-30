from typing import Dict, List, Any

from wykop import WykopAPI
from wykop.api.exceptions import EntryDoesNotExistError


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

    def add_entry(self, item_id, comments_count):
        self.entries[item_id] = {'comments_count': comments_count}
        self.entries[item_id]['comments'] = [{'id': f'sub-id-{x}'} for x in range(0, comments_count)]

    def message_send(self, receiver: str, message: str):
        if receiver not in self.conversations:
            self.conversations[receiver] = []
        if receiver not in self.conversations_summary:
            self.conversations_summary[receiver] = {'receiver': {'login': receiver}}
        self.conversations[receiver].append(message_sent(message))

    def set_entry_comments_count(self, entry_id, comments_count):
        self.entries[entry_id]['comments_count'] = comments_count
        self.entries[entry_id]['comments'] = [{'id': f'sub-id-{x}'} for x in range(0, comments_count)]

    def add_comment_to_entry(self, entry_id):
        comments_count = self.entries[entry_id]['comments_count']
        self.entries[entry_id]['comments_count'] = comments_count + 1
        self.entries[entry_id]['comments'] = [{'id': f'sub-id-{x}'} for x in range(0, comments_count)]

    def conversations_list(self) -> List[Dict[str, str]]:
        return list(self.conversations_summary.values())

    def conversation(self, receiver: str):
        return self.conversations[receiver]

    def receive_message(self, sender: str, message: str):
        if sender not in self.conversations:
            self.conversations[sender] = []
        if sender not in self.conversations_summary:
            self.conversations_summary[sender] = {'receiver': {'login': sender}}
        self.conversations[sender].append(message_received(message))

    def entry_delete(self, entry_id: str):
        self.entries.pop(entry_id)


def notification(login: str, item_id, subitem_id):
    return {
        'author': {'login': login},
        'item_id': item_id,
        'subitem_id': subitem_id,
        'new': True,
        'type': 'entry_comment_directed'
    }


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
