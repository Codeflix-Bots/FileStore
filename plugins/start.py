import os
import asyncio
import humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

# Auto-delete time in seconds (can change this as per your requirements)
FILE_AUTO_DELETE = 3600  # 1 hour for example
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)  # Convert to human-readable format

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return

        temp_msg = await message.reply("ᴡᴀɪᴛ ʙʀᴏᴏ...")

        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        # Capture the start command part for the "Get File Again" button
        start_command_part = text.split(" ", 1)[0] if len(text.split(" ", 1)) > 0 else None

        # Send the requested messages to the user
        for msg in messages:
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                # Save message for deletion later
                if start_command_part:  # Store the message to delete later
                    asyncio.create_task(delete_file_after_time(copied_msg, client, start_command_part))
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
            except:
                pass

        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚡️ ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton('🍁 sᴇʀɪᴇsғʟɪx', url='https://t.me/nova_flix/40')
                ]
            ]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
        return

# Auto-delete function and "Get File Again" button
async def delete_file_after_time(message, client, start_command_part):
    await asyncio.sleep(FILE_AUTO_DELETE)
    
    # Delete the file
    try:
        await client.delete_messages(chat_id=message.chat.id, message_ids=[message.id])
    except Exception as e:
        print(f"Error deleting message: {e}")
    
    # Create a button to "Get File Again"
    if start_command_part:
        button_url = f"https://t.me/{client.username}?start={start_command_part}"
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]
            ]
        )
    else:
        keyboard = None

    # Send a message informing the user the file is deleted and provide the "Get File Again" button
    await client.send_message(
        chat_id=message.chat.id,
        text="<b><i>Your file has been deleted automatically after the specified time. You can get it again below:</i></b>",
        reply_markup=keyboard
    )

# Function for non-subscribed users to prompt them to join the channel
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink2),
        ],
        [
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink4),
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )
