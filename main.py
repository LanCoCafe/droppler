from os import getenv

from dotenv import load_dotenv
from flask import Flask, request, abort, redirect
from langchain_anthropic import ChatAnthropic
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

from process_messages import process_group_message, process_user_message

load_dotenv()

app = Flask(__name__)

configuration = Configuration(access_token=getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(getenv("CHANNEL_SECRET"))

api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

model = ChatAnthropic(model="claude-3-5-sonnet-20240620", api_key=getenv("ANTHROPIC_API_KEY"))


@app.route("/", methods=['GET'])
def root():
    return redirect("https://wolf-yuan.dev", code=301)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    if not event.source:
        return

    elif event.source.type == "user":
        process_user_message(line_bot_api, event)

    elif event.source.type == "group":
        process_group_message(line_bot_api, event, model)

    else:
        return


if __name__ == "__main__":
    app.run(host=getenv("HOST"), port=getenv("PORT"))
