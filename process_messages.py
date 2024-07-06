import json

from google.generativeai import GenerativeModel
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, TextMessage
from linebot.v3.webhooks import MessageEvent
from pydantic import Field
from pydantic.v1 import BaseModel


class FactCheckingNeeded(BaseModel):
    needed: bool = Field(description="Whether fact-checking is needed")
    reason: str = Field(description="The reason why fact-checking is needed in Traditional Chinese")


def process_user_message(api: MessagingApi, event: MessageEvent):
    api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(
                    text="本機器人只能於群組內使用。請把我加進一個群組再試一次"
                    # TODO: Edit this text to make it more friendly
                )
            ]
        )
    )


def process_group_message(api: MessagingApi, event: MessageEvent, model: GenerativeModel):
    conversation = model.start_chat()

    response = conversation.send_message(
        "This is a message from a casual group chat. Please tell if the fact checking is needed, and the reason that fact checking is needed. \n"
        f"Message: {event.message.text}\n"
        "Output in the following json format:\n"
        """
        {
          "needed": true,
          "reason": "The reason why fact-checking is needed in Traditional Chinese, null if not needed."
        }
        """
    )

    response_dict = json.loads(response.text)
    print(response_dict)

    api.reply_message_with_http_info(
        reply_message_request=ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=str(response_dict))]
        )
    )
