from typing import Dict, List

from wykop import WykopAPI


def notification(login: str, item_id, subitem_id):
    return {
        'author': {'login': login},
        'item_id': item_id,
        'subitem_id': subitem_id,
        'new': True,
        'type': 'entry_comment_directed'
    }


class FakeWykopApi(WykopAPI):

    def __init__(self):
        super().__init__('appkey', 'secretkey')
        self.notifications: Dict[int, list] = {}
        self.entries: Dict[int, Dict[str, int]] = {}
        self.sent_messages: Dict[str, List[str]] = {}

    def notifications_direct(self, page=1):
        if page not in self.notifications:
            return []
        return self.notifications[page]

    def notification_mark_all_as_read(self):
        for key in self.notifications.keys():
            for n in self.notifications[key]:
                n['new'] = False

    def authenticate(self, account_key=None):
        pass

    def entry(self, entry_id):
        if entry_id in self.entries:
            return self.entries[entry_id]

    def add_notification(self, login: str, item_id, subitem_id, page):
        if page not in self.notifications:
            self.notifications[page] = []
        self.notifications[page].append(notification(login, item_id, subitem_id))

    def add_entry(self, item_id, comments_count):
        self.entries[item_id] = {'comments_count': comments_count}

    def send_message(self, receiver: str, message: str):
        if receiver not in self.sent_messages:
            self.sent_messages[receiver] = []
        self.sent_messages[receiver].append(message)

    def set_entry_comments_count(self, item_id, comments_count):
        self.entries[item_id]['comments_count'] = comments_count

    def get_sent_messages(self) -> Dict[str, List[str]]:
        return self.sent_messages
