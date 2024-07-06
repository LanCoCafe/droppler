from os import getenv

from dotenv import load_dotenv
from flask import Flask, request, abort, redirect
from google import generativeai
from google.generativeai import GenerativeModel
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

from src.process_messages import process_group_message, process_user_message

load_dotenv()

app = Flask(__name__)

configuration = Configuration(access_token=getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(getenv("CHANNEL_SECRET"))

api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)


def setup_gemini() -> GenerativeModel:
    generativeai.configure(api_key=getenv("GEMINI_API_KEY"))
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json",
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE"
        },
    ]

    return GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        safety_settings=safety_settings
    )


model = setup_gemini()


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
