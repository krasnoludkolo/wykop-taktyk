from typing import Dict


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

