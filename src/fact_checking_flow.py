import json

from google.generativeai import ChatSession
from linebot.v3.messaging import TextMessage


def is_fact_checking_needed(conversation: ChatSession, message: str) -> dict:
    response = conversation.send_message(
        "This is a message from a casual group chat. Please tell if the fact checking is needed, and the reason that fact checking is needed. \n"
        f"Message: {message}\n"
        "Output in the following json format:\n"
        """
        {
          "needed": true,
          "reason": "The reason why fact-checking is needed in Traditional Chinese, null if not needed."
        }
        """
    )

    return json.loads(response.text)


def tag_message(conversation: ChatSession, message: str) -> dict:
    # TODO: Implement the 2nd step of the fact-checking flow
    pass


def generate_keywords(conversation: ChatSession, message: str) -> dict:
    # TODO: Implement the 3rd step of the fact-checking flow
    pass


def search(keywords: list[str]) -> list[str]:
    # TODO: Implement the 4th step of the fact-checking flow
    pass


def check_facts(conversation: ChatSession, message: str, search_result) -> TextMessage:
    # TODO: Implement the 5th step of the fact-checking flow
    pass
