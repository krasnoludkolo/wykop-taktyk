from typing import List, Dict, Any
from itertools import takewhile

ConversationMessage = Dict[str, Any]
ConversationSummary = Dict[str, Any]
Conversation = List[ConversationMessage]
Notification = Dict[str, Any]
ConversationsList = List[ConversationSummary]
Notifications = List[Notification]


def all_new(notifications: Notifications):
    if len(notifications) == 0:
        return False
    for notification in notifications:
        if not notification['new']:
            return False
    return True


def is_last_message_received(conversation: Conversation) -> bool:
    last_message = conversation[-1]
    return is_received_message(last_message)


def get_login_from_conversation_summary(conversation: ConversationSummary) -> str:
    return conversation['receiver']['login']


def is_received_message(message: ConversationMessage):
    return message['direction'] == 'received'


def take_last_received_messages(conversation: Conversation) -> List[ConversationMessage]:
    conversation.reverse()
    return list(takewhile(is_received_message, conversation))


def take_messages_body(conversation: Conversation) -> List[str]:
    return [m['body'] for m in conversation]
