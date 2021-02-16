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


def observation_request_comment_index(entry: Entry, comment_id: str) -> int:
    return [str(c['id']) for c in entry['comments']].index(comment_id)


def comment_count_from_entry(entry: Entry) -> int:
    return entry['comments_count']


def body_from_comment_with_id(entry: Entry, comment_id) -> str:
    return next((c['body'] for c in entry['comments'] if str(c['id']) == str(comment_id)))


def comment_infos_from_entry(entry: Entry) -> List[Tuple[str, str, str]]:
    return [parse_comment(comment) for comment in entry['comments']]


def parse_comment(comment) -> Tuple[str, str, str]:
    if 'body' in comment:
        return comment['id'], comment['author']['login'], comment['body']
    else:
        return comment['id'], comment['author']['login'], ''


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
