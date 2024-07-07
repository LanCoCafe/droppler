import logging

from google.generativeai import GenerativeModel
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, TextMessage
from linebot.v3.webhooks import MessageEvent
from pydantic import Field
from pydantic.v1 import BaseModel
from pymongo.database import Database

from src.commands import dispatch_command
from src.fact_checking_flow import is_fact_checking_needed, tag_message, generate_keywords, keywords_search, check_facts
from src.models.group_settings import GroupSettings
from src.static import tags


class FactCheckingNeeded(BaseModel):
    needed: bool = Field(description="Whether fact-checking is needed")
    reason: str = Field(description="The reason why fact-checking is needed in Traditional Chinese")


def process_user_message(api: MessagingApi, event: MessageEvent):
    api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(
                    text="嘿，很高興看到你！但是你只能在一個群組裡面使用我，把我加到一個群組之後再試試一次吧"
                )
            ]
        )
    )


def process_group_message(database: Database, api: MessagingApi, event: MessageEvent, model: GenerativeModel):
    if dispatch_command(database, api, event):
        return

    group_settings = GroupSettings.find_one(api, database, group_id=event.source.group_id)
    print(f"Fetched group settings: {group_settings.to_dict()}")

    chat = model.start_chat()

    # Is fact-checking needed?
    fact_checking_needed = is_fact_checking_needed(chat, event.message.text)
    print(f"Fact-checking needed: {fact_checking_needed['reason']}")

    if not fact_checking_needed['needed']:
        return

    # Tag the message
    message_tag = tag_message(chat, event.message.text)

    if not message_tag["tag"] in group_settings.allowed_tags:
        return

    keywords = generate_keywords(chat, event.message.text)['keywords']
    print(f"Keywords: {keywords}")
    search_results = keywords_search(keywords)
    print(f"Search results: {search_results}")
    summaries = check_facts(chat, event.message.text, search_results)
    print(f"Summaries: {summaries}")

    output = TextMessage(
        text="我偵測到你的訊息有疑似需要查證的內容，因此我呼叫了小精靈們在網路上搜尋並分析了相關資訊，以下是他們給我的報告\n\n"
             f"關鍵字：{['#' + keyword for keyword in keywords]}\n"
             f"標籤：{tags[message_tag['tag']]}\n\n"
             f"這則訊息{'不是' if summaries['genuine'] else '可能是'}假訊息\n"
             f"原因：{summaries['reason']}",
        quote_token=event.message.quote_token
    )

    api.reply_message_with_http_info(
        reply_message_request=ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[output]
        )
    )
