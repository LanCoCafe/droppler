import json

from google.generativeai import ChatSession
from linebot.v3.messaging import TextMessage


def is_fact_checking_needed(conversation: ChatSession, message: str) -> dict:
    response = conversation.send_message(
        f"""
        This is a message from a casual group chat.
        Please tell if the fact checking is needed, and the reason that fact checking is needed.
        Message: {message}
        Output in the following json format:
        {
            "needed": true,
            "reason": "The reason why fact-checking is needed in Traditional Chinese, null if not needed."
        }
        """
    )

    return json.loads(response.text)


def tag_message(conversation: ChatSession, message: str) -> dict:
    response = conversation.send_message(
        f"""
        Please tag this message based on this piece of text.
        Message: {message}
        Output in the following json format:
        {
            "tags": [
                "An array of tags detected in Traditional Chinese",
                "Example: 新聞",
                "Another Example: 政治",
                "Yet Another Example: 醫療資訊"
            ]
        }
        """
    )

    return json.loads(response.text)


def generate_keywords(conversation: ChatSession, message: str) -> dict:
    response = conversation.send_message(
        f"""
        Please provide keywords that probably able to find related news to this message
        Message: {message}
        Output in the following json format:
        {
            "keywords": [
                "An array of keywords predicted in Traditional Chinese",
                "Example: 台灣近日颱風",
                "Another Example: 果菜價格",
                "Yet Another Example: 醫療量能不足"
            ]
        }
        """
    )

    return json.loads(response.text)


def search(keywords: list[str]) -> list[str]:
    # TODO: Implement the 4th step of the fact-checking flow
    pass


def check_facts(conversation: ChatSession, message: str, search_result) -> TextMessage:
    # TODO: Implement the 5th step of the fact-checking flow
    pass
