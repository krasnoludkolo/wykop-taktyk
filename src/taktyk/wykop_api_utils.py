from itertools import takewhile
from typing import List, Dict, Any, Tuple

ConversationMessage = Dict[str, Any]
ConversationSummary = Dict[str, Any]
Conversation = List[ConversationMessage]
Notification = Dict[str, Any]
Entry = Dict[str, Any]
ConversationsList = List[ConversationSummary]
Notifications = List[Notification]

entry_url = 'https://www.wykop.pl/wpis'


def all_new(notifications: Notifications) -> bool:
    if len(notifications) == 0:
        return False
    for notification in notifications:
        if not is_notification_new(notification):
            return False
    return True


def is_notification_new(notification: Notification) -> bool:
    return notification['new']


def is_notification_comment_directed(notification: Notification) -> bool:
    return notification['type'] == 'entry_comment_directed'


def observation_data_from_notification(n: Notification) -> Tuple[str, str, str]:
    login = n['author']['login']
    comment_id = n['subitem_id']
    entry_id = n['item_id']
    return entry_id, login, comment_id


def comment_count_from_entry(entry: Entry) -> int:
    return entry['comments_count']


def body_from_comment_with_id(entry: Entry, comment_id) -> str:
    return next((c['body'] for c in entry['comments'] if str(c['id']) == comment_id))


def last_comment_id_from_entry(entry: Entry) -> str:
    return entry['comments'][-1]['id']


def last_author_login_from_entry(entry: Entry) -> str:
    return entry['comments'][-1]['author']['login']


def comment_authors_with_comment_id_from_entry(entry: Entry) -> List[Tuple[str, str]]:
    return [(comment['author']['login'], comment['id']) for comment in entry['comments']]


def op_from_entry(entry: Entry) -> str:
    return entry['author']['login']


def is_last_message_received(conversation: Conversation) -> bool:
    last_message = conversation[-1]
    return is_received_message(last_message)


def get_login_from_conversation_summary(conversation: ConversationSummary) -> str:
    return conversation['receiver']['login']


def is_received_message(message: ConversationMessage):
    return message['direction'] == 'received'


def take_new_messages(conversation: Conversation) -> List[ConversationMessage]:
    conversation.reverse()
    return list(takewhile(is_received_message, conversation))


def take_messages_body(conversation: Conversation) -> List[str]:
    return [m['body'] for m in conversation]
