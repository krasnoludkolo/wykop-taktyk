from typing import Dict

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
        self.entries: Dict[int, object] = {}

    def notifications_direct(self, page=1):
        if page not in self.notifications:
            return []
        return self.notifications[page]

    def notification_mark_all_as_read(self):
        # TODO
        pass

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
