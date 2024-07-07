import json

from google.generativeai import ChatSession
from googlesearch import search
from linebot.v3.messaging import TextMessage

from src.static import tags
from src.utils import parse_news_url


def is_fact_checking_needed(conversation: ChatSession, message: str) -> dict:
    response = conversation.send_message(
        f"""
        This is a message from a casual group chat.
        Please tell if the fact checking is needed, and the reason that fact checking is needed.
        Message: {message}
        Output in the following json format:""" + """
        ```json
        {
            "needed": true,
            "reason": "The reason why fact-checking is needed in Traditional Chinese, null if not needed."
        }
        ```
        """
    )

    return json.loads(response.text)


def tag_message(conversation: ChatSession, message: str) -> dict:
    response = conversation.send_message(
        f"""
        Categorize the message with one of the following tags
        {tags}
        Match as much as possible.
        Message: {message}
        Output in the following json format:
        """ + """
        ```json
        {
            "tag": 0
        }
        ```
        """
    )

    return json.loads(response.text)


def generate_keywords(conversation: ChatSession, message: str) -> dict:
    response = conversation.send_message(
        f"""
        Please provide keywords that probably able to find related news to this message
        Message: {message}
        Output in the following json format:
        """ + """
        ```json
        {
            "keywords": [
                "An array of keywords predicted in Traditional Chinese",
                "Example: 台灣近日颱風",
                "Another Example: 果菜價格",
                "Yet Another Example: 醫療量能不足"
            ]
        }
        ```
        """
    )

    return json.loads(response.text)


def keywords_search(keywords: list[str]) -> list[dict[str, str | bool]]:
    """
    Search for news related to a list of keywords.

    Args:
        keywords (List[str]): A list of keywords to search for.

    Returns:
        List[Dict[str, bool]]: A list of dictionaries containing the result of parsing each news link.
    """
    result = []
    for keyword in keywords:
        for link in search(keyword, stop=5, pause=1.0):
            result.append(parse_news_url(link))
    return result


def check_facts(conversation: ChatSession, message: str, search_result) -> TextMessage:
    # TODO: Implement the 5th step of the fact-checking flow
    pass
