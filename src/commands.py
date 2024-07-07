from linebot.v3.messaging import MessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent
from pymongo.database import Database

from src.models.group_settings import GroupSettings
from src.static import tags


def dispatch_command(database: Database, api: MessagingApi, event: MessageEvent) -> bool:
    """
    Dispatches the commands with the given event.

    :param database:
    :param api:
    :param event:
    :return: True if a command is dispatched, False otherwise.
    """
    command_parts = event.message.text.strip().split(" ")

    command = command_parts[0]

    if command == "/tags":
        configure_tags(database, api, event, command_parts[1:])
        return True
    else:
        return False


def configure_tags(database: Database, api: MessagingApi, event: MessageEvent, args: list[str]):
    """
    Configures the tags for the group.

    :param database:
    :param api:
    :param event:
    :param args:
    """
    group_id = event.source.group_id

    if not args:
        group_settings = GroupSettings.find_one(api, database, group_id=group_id)

        if not group_settings:
            api.reply_message_with_http_info(
                reply_message_request=ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="這個群組沒有設定任何標籤")]
                )
            )
            return

        api.reply_message_with_http_info(
            reply_message_request=ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(
                    text=f"這個群組的標籤是\n{', '.join([tags[tag] for tag in group_settings.allowed_tags])}"
                )]
            )
        )

        return

    unavailable_tags = []

    specified_tags = []

    for tag in args:
        try:
            if int(tag) in tags:
                specified_tags.append(int(tag))
            continue
        except ValueError:
            pass

        unavailable_tags.append(tag)

    if unavailable_tags:
        api.reply_message_with_http_info(
            reply_message_request=ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=f"以下標籤不可用\n{unavailable_tags}\n請提供一個或以上有效的標籤，用空格分隔\n{tags}"
                    )]
            )
        )
        return

    group_settings = GroupSettings(
        api,
        database,
        group_id,
        specified_tags
    )

    group_settings.upsert()

    api.reply_message_with_http_info(
        reply_message_request=ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=f"已為這個群組設定了允許的標籤\n{', '.join([tags[tag] for tag in group_settings.allowed_tags])}")]
        )
    )
