import base64
import re
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, Forbidden, PeerIdInvalid, ChatAdminRequired, FloodWait
from datetime import datetime, timedelta
from pyrogram import errors

#===============================================================#

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

#===============================================================#

async def decode(base64_string):
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

#===============================================================#

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            # Use new multi-DB channel function
            msgs = await get_messages_from_db_channels(client, temb_ids)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await get_messages_from_db_channels(client, temb_ids)
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

#===============================================================#

async def get_message_id(client, message):
    """Get message ID and source channel ID from forwarded message or link"""
    if message.forward_from_chat:
        # Check if forwarded from primary DB channel
        if message.forward_from_chat.id == client.db:
            return message.forward_from_message_id, client.db
        # Check against multiple DB channels
        db_channels = getattr(client, 'db_channels', {})
        for channel_id_str in db_channels.keys():
            if message.forward_from_chat.id == int(channel_id_str):
                return message.forward_from_message_id, int(channel_id_str)
        return 0, 0
    elif message.forward_sender_name:
        return 0, 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0, 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            # Check primary DB channel
            if f"-100{channel_id}" == str(client.db):
                return msg_id, client.db
            # Check against multiple DB channels
            db_channels = getattr(client, 'db_channels', {})
            for channel_id_str in db_channels.keys():
                if f"-100{channel_id}" == channel_id_str:
                    return msg_id, int(channel_id_str)
        else:
            # Check by username for primary DB channel
            if hasattr(client, 'db_channel') and channel_id == client.db_channel.username:
                return msg_id, client.db
            # Check against multiple DB channels usernames (if needed)
            db_channels = getattr(client, 'db_channels', {})
            for channel_id_str, channel_data in db_channels.items():
                try:
                    chat = await client.get_chat(int(channel_id_str))
                    if hasattr(chat, 'username') and chat.username == channel_id:
                        return msg_id, int(channel_id_str)
                except:
                    continue
    else:
        return 0, 0


#===============================================================#

async def get_message_id_legacy(client, message):
    """Legacy function for backward compatibility - returns only message ID"""
    msg_id, _ = await get_message_id(client, message)
    return msg_id


#===============================================================#

async def get_messages_from_db_channels(client, temb_ids):
    """Get messages from multiple DB channels - tries primary first, then falls back to others"""
    messages = []
    total_messages = 0
    
    # First try primary DB channel
    try:
        primary_db = getattr(client, 'primary_db_channel', client.db)
        msgs = await client.get_messages(
            chat_id=primary_db,
            message_ids=temb_ids
        )
        # Filter out None messages (deleted/not found)
        valid_msgs = [msg for msg in msgs if msg is not None]
        messages.extend(valid_msgs)
        found_ids = {msg.id for msg in valid_msgs}
        missing_ids = [mid for mid in temb_ids if mid not in found_ids]
        
        # If we found all messages, return early
        if not missing_ids:
            return messages
        
        # Try other DB channels for missing messages
        db_channels = getattr(client, 'db_channels', {})
        for channel_id_str, channel_data in db_channels.items():
            if not channel_data.get('is_active', True):  # Skip inactive channels
                continue
            if int(channel_id_str) == primary_db:  # Skip primary (already tried)
                continue
                
            try:
                additional_msgs = await client.get_messages(
                    chat_id=int(channel_id_str),
                    message_ids=missing_ids
                )
                valid_additional = [msg for msg in additional_msgs if msg is not None]
                messages.extend(valid_additional)
                
                # Update missing IDs
                found_additional_ids = {msg.id for msg in valid_additional}
                missing_ids = [mid for mid in missing_ids if mid not in found_additional_ids]
                
                # If we found all remaining messages, break
                if not missing_ids:
                    break
                    
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Error getting messages from DB channel {channel_id_str}: {e}")
                continue
        
    except FloodWait as e:
        await asyncio.sleep(e.x)
        # Retry with the same function
        return await get_messages_from_db_channels(client, temb_ids)
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Error getting messages from DB channels: {e}")
    
    return messages

#===============================================================#

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

#===============================================================#

async def is_bot_admin(client, channel_id):
    try:
        bot = await client.get_chat_member(channel_id, "me")
        if bot.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            if bot.privileges:
                required_rights = ["can_invite_users", "can_delete_messages"]
                missing_rights = [right for right in required_rights if not getattr(bot.privileges, right, False)]
                if missing_rights:
                    return False, f"Bot is missing the following rights: {', '.join(missing_rights)}"
            return True, None
        return False, "Bot is not an admin in the channel."
    except errors.ChatAdminRequired:
        return False, "Bot lacks perminsion to access admin information in this channel."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

#===============================================================#

async def check_subscription(client, user_id):
    """Enhanced subscription check with better request channel handling."""
    statuses = {}

    # Ensure user exists in database
    if not await client.mongodb.present_user(user_id):
        await client.mongodb.add_user(user_id)

    for channel_id, (channel_name, channel_link, request, timer) in client.fsub_dict.items():
        try:
            # Get actual membership status first
            user = await client.get_chat_member(channel_id, user_id)
            actual_status = user.status
            
            # If user is already a member, admin, or owner
            if actual_status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                await client.mongodb.update_fsub_status(user_id, channel_id, "joined")
                await client.mongodb.add_channel_user(channel_id, user_id)
                
                # If there was a pending join request, mark it as approved
                if request and await client.mongodb.has_submitted_join_request(user_id, channel_id):
                    await client.mongodb.update_join_request_status(user_id, channel_id, "approved")
                
                statuses[channel_id] = actual_status
                continue
            
            # User is not a member - check if they left after being approved  
            if request:
                # For request channels, check if user has submitted a request
                has_request = await client.mongodb.has_submitted_join_request(user_id, channel_id)
                if has_request:
                    # User has submitted request but not yet a member
                    request_status = await client.mongodb.get_join_request_status(user_id, channel_id)
                    
                    if request_status == "approved":
                        # Request was approved but user still not in channel
                        # This means user might have left after approval - force them to rejoin
                        await client.mongodb.update_fsub_status(user_id, channel_id, "left")
                        await client.mongodb.remove_join_request(user_id, channel_id)
                        statuses[channel_id] = ChatMemberStatus.BANNED
                    else:
                        # Request is still pending, allow user to proceed
                        await client.mongodb.update_fsub_status(user_id, channel_id, "request_submitted")
                        statuses[channel_id] = ChatMemberStatus.MEMBER  # Treat as subscribed for request channels
                else:
                    # No request submitted yet for request channel
                    await client.mongodb.update_fsub_status(user_id, channel_id, "not_requested")
                    statuses[channel_id] = ChatMemberStatus.BANNED
            else:
                # Regular channel (not request), user must be a member
                await client.mongodb.update_fsub_status(user_id, channel_id, "left")
                await client.mongodb.remove_channel_user(channel_id, user_id)
                statuses[channel_id] = ChatMemberStatus.BANNED
                
        except UserNotParticipant:
            # User is not in the channel
            await client.mongodb.update_fsub_status(user_id, channel_id, "left")
            await client.mongodb.remove_channel_user(channel_id, user_id)
            
            if request:
                # For request channels, check if user has submitted a request
                has_request = await client.mongodb.has_submitted_join_request(user_id, channel_id)
                if has_request:
                    # User has submitted request but not in channel - still allow access for request channels
                    await client.mongodb.update_fsub_status(user_id, channel_id, "request_submitted")
                    statuses[channel_id] = ChatMemberStatus.MEMBER  # Treat as subscribed for request channels
                else:
                    # No request submitted yet
                    await client.mongodb.update_fsub_status(user_id, channel_id, "not_requested")
                    statuses[channel_id] = ChatMemberStatus.BANNED
            else:
                # Regular channel, user must join
                statuses[channel_id] = ChatMemberStatus.BANNED
                
        except Forbidden:
            client.LOGGER(__name__, client.name).warning(f"Bot lacks permission for {channel_name}.")
            statuses[channel_id] = None
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error checking {channel_name}: {e}")
            statuses[channel_id] = None

    return statuses

#===============================================================#

def is_user_subscribed(statuses):
    """Check if user is subscribed to all channels."""
    return all(
        status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
        for status in statuses.values() if status is not None
    ) and bool(statuses)

#===============================================================#

def force_sub(func):
    """Decorator to enforce force subscription before executing a command."""
    async def wrapper(client: Client, message: Message):
        if not client.fsub_dict:
            return await func(client, message)
        photo = client.messages.get('FSUB_PHOTO', '')
        if photo:
            msg = await message.reply_photo(
                caption="<b>ᴡᴀɪᴛ ᴀ sᴇᴄᴏɴᴅ.....</b>", 
                photo=photo
            )
        else:
            msg = await message.reply(
                "<code><b>ᴡᴀɪᴛ ᴀ sᴇᴄᴏɴᴅ.....</b></code>"
            )
        user_id = message.from_user.id
        statuses = await check_subscription(client, user_id)

        if is_user_subscribed(statuses):
            await msg.delete()
            return await func(client, message)

        # User is not subscribed to all channels
        buttons = []
        channels_message = f"{client.messages.get('FSUB', '')}\n\n"

        for channel_id, (channel_name, channel_link, request, timer) in client.fsub_dict.items():
            status = statuses.get(channel_id, None)

            # Generate invite link if needed
            if timer > 0:
                expire_time = datetime.now() + timedelta(minutes=timer)
                try:
                    invite = await client.create_chat_invite_link(
                        chat_id=channel_id,
                        expire_date=expire_time,
                        creates_join_request=request
                    )
                    channel_link = invite.invite_link
                except Exception as e:
                    client.LOGGER(__name__, client.name).warning(f"Error creating invite link for {channel_name}: {e}")

            # Add button based on user status
            if status not in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                # Check if user has already submitted request for request channels
                if request and await client.mongodb.has_submitted_join_request(user_id, channel_id):
                    request_status = await client.mongodb.get_join_request_status(user_id, channel_id)
                    if request_status == "pending":
                        # Don't add button if request is still pending
                        continue
                    elif request_status == "approved":
                        # User can now join the channel
                        button_text = f"{channel_name}"
                    else:
                        button_text = f"{channel_name}"
                else:
                    # User hasn't submitted request or it's a regular channel
                    if request:
                        button_text = f"{channel_name}"
                    else:
                        button_text = f"{channel_name}"
                
                buttons.append(InlineKeyboardButton(button_text, url=channel_link))

        # Add "Try Again" button if needed
        from_link = message.text.split(" ")
        if len(from_link) > 1:
            try_again_link = f"https://t.me/{client.username}/?start={from_link[1]}"
            buttons.append(InlineKeyboardButton("🔄 Try Again", url=try_again_link))

        # Organize buttons in rows of 1 for better readability
        buttons_markup = InlineKeyboardMarkup([[button] for button in buttons])
        buttons_markup = None if not buttons else buttons_markup

        # Edit message with status update and buttons
        try:
            await msg.edit_text(text=channels_message, reply_markup=buttons_markup)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error updating force sub message: {e}")
            # Fallback: send new message if edit fails
            try:
                await msg.delete()
                await message.reply(text=channels_message, reply_markup=buttons_markup)
            except Exception:
                pass

    return wrapper

#===============================================================#

#Time conversion for auto delete timer
def convert_time(duration_seconds: int) -> str:
    periods = [
        ('Yᴇᴀʀ', 60 * 60 * 24 * 365),
        ('Mᴏɴᴛʜ', 60 * 60 * 24 * 30),
        ('Day', 60 * 60 * 24),
        ('Hour', 60 * 60),
        ('Minute', 60),
        ('Second', 1)
    ]

    parts = []
    for period_name, period_seconds in periods:
        if duration_seconds >= period_seconds:
            num_periods = duration_seconds // period_seconds
            duration_seconds %= period_seconds
            parts.append(f"{num_periods} {period_name}{'s' if num_periods > 1 else ''}")

    if len(parts) == 0:
        return "0 Sᴇᴄᴏɴᴅ"
    elif len(parts) == 1:
        return parts[0]
    else:
        return ', '.join(parts[:-1]) +' ᴀɴᴅ '+ parts[-1]

#===============================================================#
#.........Auto Delete Functions.......#
#===============================================================#

DEL_MSG = """<b>This File is deleting automatically in <a href="https://t.me/{username}">{time}</a>.. Forward in your Saved Messages..!</b>"""

#Function for provide auto delete notification message
async def auto_del_notification(bot_username, msg, delay_time, transfer): 
    temp = await msg.reply_text(DEL_MSG.format(username=bot_username, time=convert_time(delay_time)), disable_web_page_preview = True) 

    await asyncio.sleep(delay_time)
    try:
        if transfer:
            try:
                name = "• ɢᴇᴛ ғɪʟᴇs •"
                link = f"https://t.me/{bot_username}?start={transfer}"
                button = [[InlineKeyboardButton(text=name, url=link), InlineKeyboardButton(text="ᴄʟᴏsᴇ •", callback_data = "close")]]

                await temp.edit_text(text=f"<b>›› Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ\n\nIғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: <a href={link}>{name}</a> ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</b>", reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview = True)

            except Exception as e:
                await temp.edit_text(f"<b>›› Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ </b>")
                print(f"Error occured while editing the Delete message: {e}")
        else:
            await temp.edit_text(f"<b>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ </b>")

    except Exception as e:
        print(f"Error occured while editing the Delete message: {e}")
        await temp.edit_text(f"<b>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ </b>")

    try: await msg.delete()
    except Exception as e: print(f"Error occurred on auto_del_notification() : {e}")

#Function for deleteing files/Messages.....
async def delete_message(msg, delay_time): 
    await asyncio.sleep(delay_time)
    
    try: await msg.delete()
    except Exception as e: print(f"Error occurred on delete_message() : {e}")

#===============================================================#

#Function for batch auto delete - sends one notification for all files
async def batch_auto_del_notification(bot_username, messages, delay_time, transfer_link, chat_id, client):
    """Send one notification for batch of files and delete all after timer"""
    if not messages:
        return
        
    # Send single countdown notification
    notification_msg = await client.send_message(
        chat_id=chat_id,
        text=DEL_MSG.format(username=bot_username, time=convert_time(delay_time)),
        disable_web_page_preview=True
    )
    
    await asyncio.sleep(delay_time)
    
    # Delete all file messages
    for msg in messages:
        try:
            await msg.delete()
        except Exception as e:
            print(f"Error deleting message {getattr(msg, 'id', 'Unknown')}: {e}")
    
    # Update notification with get files button
    try:
        if transfer_link:
            try:
                name = "• ɢᴇᴛ ғɪʟᴇs •"
                link = f"https://t.me/{bot_username}?start={transfer_link}"
                button = [[InlineKeyboardButton(text=name, url=link), InlineKeyboardButton(text="ᴄʟᴏsᴇ •", callback_data="close")]]
                
                await notification_msg.edit_text(
                    text=f"<b>›› Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ\n\nIғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: <a href={link}>{name}</a> ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</b>",
                    reply_markup=InlineKeyboardMarkup(button),
                    disable_web_page_preview=True
                )
            except Exception as e:
                await notification_msg.edit_text(f"<b>›› Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ</b>")
                print(f"Error editing notification message: {e}")
        else:
            await notification_msg.edit_text(f"<b>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ</b>")
    except Exception as e:
        print(f"Error updating notification message: {e}")
