from aiogram import Bot, Dispatcher, executor, types
from asyncio import sleep
from json import loads
from pyrogram import Client


AIOGRAM_BOT_TOKEN = '123456123456bnmsdilhsl '

PYROGRAM_API_ID = 88888888
PYROGRAM_API_HASH = "4815313fgjlb,g;dml;jhdd"

CHAT_ID = -1004567304789

WINDOW_SIZE = 100
CHUNK_SIZE = 100

old_messages = {}


# reading the chat history
async def reading_history(window_size):
    # pyrogram bot
    async with Client("account", PYROGRAM_API_ID, PYROGRAM_API_HASH) as pyrogram_client:
        # number of messages in the history
        chat_history_count = await pyrogram_client.get_chat_history_count(CHAT_ID)

        if window_size < chat_history_count:
            messages_to_read_number = window_size
        else:
            messages_to_read_number = chat_history_count

        messages = {}

        # reading the messages from the history in parts
        for offset in range(0, messages_to_read_number, CHUNK_SIZE):
            chat_history = pyrogram_client.get_chat_history(
                chat_id=CHAT_ID,
                limit=CHUNK_SIZE,
                offset=offset
            )

            async for message in chat_history:
                row = loads(str(message))
                if '_' in row:
                    if row['_'] == 'Message':
                        messages[row['id']] = row

            # pause to bypass telegram protection
            if offset % (20 * CHUNK_SIZE) == 0 and offset > 0:
                # pause
                await sleep(30)
            await sleep(1)

    return messages


# aiogram bot init
bot = Bot(token=AIOGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


# reaction to a new message
@dp.message_handler()
async def new_message(message: types.Message):
    global old_messages

    # checking the chat ID
    if message.chat.id != CHAT_ID:
        return

    # adding new messages to the dictionary
    row = loads(str(message))
    old_messages[row['message_id']] = row

    # deleting messages that are too old from the dictionary
    if len(old_messages) > WINDOW_SIZE:
        del old_messages[min(old_messages.keys())]

    # the command detection and create report
    if "/deleted" in message.text:
        await report_on_deleted_messages()


async def report_on_deleted_messages():
    global old_messages

    current_messages = await reading_history(WINDOW_SIZE * 2)

    deleted_messages = set(old_messages) - set(current_messages)

    for i in deleted_messages:
        try:
            text = f'from user "{old_messages[i]["from_user"]["username"]}"\n ' \
                   f'was delete message "{old_messages[i]["text"]}"'
        except (Exception,):
            try:
                text = f'from user {old_messages[i]["from"]["username"]} \n ' \
                       f'was deleted message "{old_messages[i]["text"]}"'
            except (Exception,):
                text = str(old_messages[i])

        report_message = await bot.send_message(CHAT_ID, text)
        report_message.text = report_message.text.replace("/", "-")

        await new_message(report_message)


async def on_startup(_):
    global old_messages

    old_messages = await reading_history(WINDOW_SIZE)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
