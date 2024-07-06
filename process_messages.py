from langchain_core.language_models import BaseChatModel
from linebot.v3.messaging import ReplyMessageRequest, MessagingApi, TextMessage
from linebot.v3.webhooks import MessageEvent

from utils import get_social_titles, NewsScore, get_news_score, extract_links


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


def process_group_message(api: MessagingApi, event: MessageEvent, model: BaseChatModel):
    links = extract_links(event.message.text)[0:5]

    if not links:
        return

    response_messages: list[TextMessage] = []

    for link in links:
        try:
            title = get_social_titles(link)
        except Exception as e:
            response_messages.append(TextMessage(text=f"Error retrieving or parsing URL: {str(e)}"))
            continue

        scores: NewsScore = get_news_score(model, title)

        response_messages.append(
            TextMessage(
                text=f"Title: {title}\n" +
                     f"Exaggerate: {scores.exaggerate}\n" if scores.exaggerate > 5 else "" +
                     f"Clickbait: {scores.clickbait}\n" if scores.clickbait > 5 else "" +
                     f"Misleading: {scores.misleading}\n" if scores.misleading > 5 else "" +
                     f"Controversy: {scores.controversy}\n" if scores.controversy > 5 else "" +
                     f"Piggyback: {scores.piggyback}\n" if scores.piggyback > 5 else "" +
                     f"Inflammatory: {scores.inflammatory}\n" if scores.inflammatory > 5 else "" +
                     f"Reason: {scores.reason}"
            )
        )

    print(response_messages)
    
    api.reply_message_with_http_info(
        reply_message_request=ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=response_messages
        )
    )
