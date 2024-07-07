from google.generativeai import GenerativeModel
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, TextMessage
from linebot.v3.webhooks import MessageEvent
from pydantic import Field
from pydantic.v1 import BaseModel
from pymongo.database import Database

from src.commands import dispatch_command
from src.fact_checking_flow import is_fact_checking_needed, tag_message
from src.models.group_settings import GroupSettings


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

    chat = model.start_chat()

    fact_checking_needed = is_fact_checking_needed(chat, event.message.text)

    if not fact_checking_needed['needed']:
        return

    fact_checking_needed_reason = fact_checking_needed['reason']

    message_tags = tag_message(chat, event.message.text)

    if not message_tags["tag"] in group_settings.allowed_tags:
        return

    api.reply_message_with_http_info(
        reply_message_request=ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=fact_checking_needed_reason)]
        )
    )
