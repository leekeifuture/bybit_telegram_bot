import asyncio
import logging
import traceback

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils import executor
from telethon import events
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, \
    UserNotMutualContactError
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl import functions
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerUser

from settings import SESSION_STRING, API_ID, API_HASH, TELEGRAM_CHAT_ID, \
    TELEGRAM_BOT_TOKEN, TELEGRAM_ADMINS

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(level='INFO')


async def check_new_users():
    while True:
        await asyncio.sleep(1)


async def is_user_in_chat(user_id):
    chat = await client.get_entity(TELEGRAM_CHAT_ID)
    await client.get_participants(chat)
    chat_members = await client.get_participants(chat)
    chat_members_id = list(map(lambda member: member.id, chat_members))
    return user_id in chat_members_id


def gen_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton('Approve', callback_data=f'approve_{user_id}'),
        InlineKeyboardButton('Deny', callback_data=f'deny_{user_id}')
    )
    return markup


@dp.callback_query_handler()  # TODO: check if from admin
async def callback_query(callback: types.CallbackQuery):
    print()
    if callback.data.startswith('approve'):
        user_id = int(callback.data.split('approve_')[1])
        user = await client.get_entity(user_id)
        chat = await client.get_entity(TELEGRAM_CHAT_ID)

        try:
            await client(
                InviteToChannelRequest(chat, [user])
            )
        except UserNotMutualContactError:
            await client.send_message(
                user,
                'You was approved to join a chat ✅,\n'
                'but you is not a mutual contact of this bot 😣\n'
                'Please add me to your telegram contacts and resend your '
                'ByBit UID 👍'
            )
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text='Error ❌\n'
                     'The provided user is not a mutual contact!\n'
                     'User was notified.',
            )
            logger.error('The provided user is not a mutual contact.')
        except PeerFloodError:
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text='Error ❌\n'
                     'Getting Flood Error from telegram. '
                     'Script is stopping now. '
                     'Please try again after some time.',
            )
            logger.error(
                'Getting Flood Error from telegram. '
                'Script is stopping now. Please try again after some time.'
            )
        except UserPrivacyRestrictedError:
            await client.send_message(
                user,
                'You was approved to join a chat ✅,\n'
                'but your privacy settings don\'t not allow to invite '
                'you to chat 😣\n'
                'Please change your settings and resend your ByBit UID 👍'
            )
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text='Error ❌\n'
                     'The user\'s privacy settings do not allow you to do '
                     'this!\n'
                     'User was notified.',
            )
            logger.error(
                'The user\'s privacy settings do not allow you to do this. '
                'Skipping.\n'
            )
        except Exception as e:
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text='Error ❌\n'
                     f'{str(e)}',
            )
            traceback.print_exc()
            logger.error('Unexpected Error')
        else:
            await client.send_message(
                user,
                'You\'re successful approved and '
                'been added to the chat ✅'
            )
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=f'{callback.from_user.full_name} has been successfully '
                     'approved and added to the chat!'
            )
            logger.info(
                user.first_name + ' has been approved by ' +
                callback.from_user.full_name
            )
    elif callback.data.startswith('deny'):
        user_id = int(callback.data.split('deny_')[1])
        user = await client.get_entity(user_id)

        await client.send_message(
            user,
            'You was denied to join to the private chat 😢'
        )
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=f'{callback.from_user.full_name} has been successfully denied!'
        )
        logger.info(user.first_name + ' has been denied by ' +
                    callback.from_user.full_name)


@client.on(events.NewMessage(func=lambda message: message.is_private))
async def handler_new_message(event):
    reply = await event.reply('Loading...')
    user = await client.get_entity(reply.input_chat)
    user_last_name = f' {user.last_name}' if user.last_name else ''
    user_full_name = user.first_name + user_last_name

    history = await client(GetHistoryRequest(
        peer=InputPeerUser(user.id, user.access_hash),
        offset_id=0,
        offset_date=None,
        add_offset=0,
        limit=1,
        max_id=0,
        min_id=0,
        hash=user.access_hash
    ))

    if history.count <= 2:
        await client.send_message(
            event.message.from_id.user_id,
            'Welcome! I\'m here to help you get access to ByBit '
            'chat. Just send me your UID from ByBit '
            'affiliates and wait a bit when someone from admins '
            'approves your request :fingers_crossed:'
        )
    elif await is_user_in_chat(event.message.from_id.user_id):
        await client.send_message(
            event.message.from_id.user_id, 'You already consist in the chat! ✅'
        )
    elif event.message.text.isdigit():
        await client(
            functions.contacts.AddContactRequest(
                id=reply.input_chat.user_id,
                first_name=user.first_name,
                last_name=user.last_name if user.last_name else '', phone='',
                add_phone_privacy_exception=False
            )
        )

        logger.info('Started processing ' + user_full_name +
                    ' with id: ' + str(user.id) +
                    ' and uid: ' + str(event.message.text))

        for admin_id in TELEGRAM_ADMINS:
            await bot.send_message(
                int(admin_id),
                '**' + user_full_name + '** sent request to join to the chat!\n'
                                        'ByBit UID: ' + event.message.text,
                reply_markup=gen_markup(event.message.from_id.user_id),
                parse_mode=ParseMode.MARKDOWN
            )

        await client.send_message(
            event.message.from_id.user_id,
            'Your request has been successfully created! '
            'Please wait up to 48 hours to approve your request 🕔'
        )

        logger.info(
            user_full_name + ' (' + str(
                user.id) + ') ' + 'is successfully processed!'
        )
    else:
        await client.send_message(
            event.message.from_id.user_id,
            'Incorrect message! Please send your ByBit UID...'
        )

    await reply.delete()


async def main():
    await client.start()
    if await client.is_user_authorized():
        me = await client.get_me()
        logger.info('---------------------------------------------------------')
        logger.info(f'Connected as {me.username} ({me.phone})')

        executor.start_polling(dp)

        await asyncio.gather(
            check_new_users(),
            client.run_until_disconnected()
        )
    else:
        logger.error('Cannot be authorized')


if __name__ == '__main__':
    loop = asyncio.get_event_loop().run_until_complete(main())
