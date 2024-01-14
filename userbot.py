import asyncio
from contextlib import suppress
from telethon import utils
from telethon import events
import re
from start_bots import logger
from config import client, bot, channel_id, db, admin_user_id


def get_triggers():
    triggers = db.fetchall("SELECT trigger FROM triggers")
    return [row[0] for row in triggers]


@client.on(events.NewMessage)
async def handler_group(event):
    try:
        if event.is_group:
            triggers = get_triggers()
            r = re.compile("|".join(triggers), flags=re.I)
            list_count = r.findall(event.raw_text)
            if len(list_count) >= 1:

                sender = await event.get_sender()
                if sender.bot:
                    return
                message = event.message
                sender_name = utils.get_display_name(sender)
                chat = await event.get_chat()
                chat_name = utils.get_display_name(chat)
                sender_username, chat_username = None, None
                with suppress(Exception):
                    sender_username = sender.username
                with suppress(Exception):
                    chat_username = chat.username
                await bot.send_message(chat_id=channel_id,
                                       text=f"{message.message}\n\n"
                                            f"Cообщение от:\n"
                                            f"Имя: <b>{sender_name}</b>\n"
                                            f"Юзернейм: <b>{f'@{sender_username}' if sender_username else 'не установлен'}</b>\n\n"
                                            f"Название чата: <b>{chat_name}</b>\n"
                                            f"Юзернейм чата: <b>{f'@{chat_username}' if chat_username else 'не установлен'}</b>\n"
                                       )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex}")
        await bot.send_message(chat_id=admin_user_id, text="На стороне сервера произошла ошибка!!!\n"
                                                           "Обратитесь к разработчику!")


async def run_client():
    await client.run_until_disconnected()


async def run_userbot():
    try:
        await asyncio.gather(
            asyncio.ensure_future(run_client())
        )
    except KeyboardInterrupt:
        print("Бот остановлен по запросу пользователя.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await client.disconnect()
