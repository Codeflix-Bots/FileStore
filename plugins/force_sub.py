from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from helper.helper_func import is_bot_admin

#===============================================================#

async def fsub(client, query):
    # Create a formatted list of channels with names and IDs
    if client.fsub_dict:
        channel_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            channel_name = channel_data[0] if channel_data and len(channel_data) > 0 else "Unknown"
            request_status = "Request: ✅" if channel_data[2] else "Request: ❌"
            timer_status = f"Timer: {channel_data[3]}m" if channel_data[3] > 0 else "Timer: ∞"
            
            # Get chat type
            try:
                chat = await client.get_chat(channel_id)
                chat_type = "Group" if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP] else "Channel"
            except:
                chat_type = "Unknown"
            
            channel_list.append(f"• `{channel_name}` (`{channel_id}`) - {chat_type}, {request_status}, {timer_status}")
        
        channels_display = "\n".join(channel_list)
    else:
        channels_display = "_No force subscription channels/groups configured_"
    
    msg = f"""<blockquote>**Force Subscription Settings:**</blockquote>
**Configured Channels/Groups:**
{channels_display}

__Use the appropriate button below to add or remove a force subscription channel/group based on your needs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ/ɢʀᴏᴜᴘ', 'add_fsub'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ', 'rm_fsub')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex('^add_fsub$'))
async def add_fsub(client: Client, query: CallbackQuery):
    await query.answer()
    ask_channel_info = await client.ask(
        query.from_user.id, 
        """Send channel/group ID (negative integer), request boolean (yes/no), timer (minutes) separated by space in the next 60 seconds!

<blockquote expandable>**Example:** `-1001234567890 yes 5`

**Explanation:**
• `-1001234567890` = Channel/Group ID
• `yes` = Enable join request mode (users send request instead of direct join)
• `5` = Invite link expires after 5 minutes (use 0 for permanent link)

**For Groups:** Make sure bot is admin with "Invite Users" permission!</blockquote>""", 
        filters=filters.text, 
        timeout=60
    )
    
    try:
        channel_info = ask_channel_info.text.split()
        channel_id, request, timer = channel_info
        channel_id = int(channel_id)
        
        if channel_id in client.fsub_dict.keys():
            return await ask_channel_info.reply("**This channel/group already exists in force sub list! Remove it to change configuration.**")
        
        # Check if bot is admin
        val, res = await is_bot_admin(client, channel_id)
        if not val:
            return await ask_channel_info.reply(f"**Error:** `{res}`\n\n**For groups, bot needs 'Invite Users' permission!**")
        
        # Parse request parameter
        if request.lower() in ('true', 'on', 'yes'):
            request = True
        elif request.lower() in ('false', 'off', 'no'):
            request = False
        else:
            raise Exception("Invalid request value. Use yes/no, true/false, or on/off.")
        
        # Parse timer
        if timer.isdigit():
            timer = int(timer)
        else:
            raise Exception("Timer must be a valid integer (minutes).")
        
        # Get chat info
        chat = await client.get_chat(channel_id)
        name = chat.title
        chat_type = chat.type
        
        # For groups with request mode, verify it's a supergroup
        if request and chat_type == ChatType.GROUP:
            return await ask_channel_info.reply(
                "**❌ Error:** Regular groups don't support join requests!\n\n"
                "**Solution:** Convert to supergroup first:\n"
                "1. Go to group settings\n"
                "2. Enable 'Group History for New Members'\n"
                "3. Group will auto-convert to supergroup"
            )
        
        # Create invite link
        if timer > 0:
            client.fsub_dict[channel_id] = [name, None, request, timer]
        else:
            try:
                chat_link = await client.create_chat_invite_link(
                    channel_id, 
                    creates_join_request=request
                )
                link = chat_link.invite_link
                client.fsub_dict[channel_id] = [name, link, request, timer]
            except Exception as e:
                return await ask_channel_info.reply(
                    f"**❌ Failed to create invite link:** `{e}`\n\n"
                    "**For groups:** Ensure bot has 'Invite Users' permission"
                )
        
        # Update req_channels list if request is enabled
        if request and channel_id not in client.req_channels:
            client.req_channels.append(channel_id)
            await client.mongodb.set_channels(client.req_channels)
        
        # Save to database
        await client.mongodb.add_fsub_channel(channel_id, client.fsub_dict[channel_id])
        
        chat_type_str = "Group" if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP] else "Channel"
        await fsub(client, query)
        return await ask_channel_info.reply(
            f"**✅ Success!**\n\n"
            f"**Name:** `{name.strip()}`\n"
            f"**Type:** {chat_type_str}\n"
            f"**Request Mode:** {'✅ Enabled' if request else '❌ Disabled'}\n"
            f"**Timer:** {timer} minutes" if timer > 0 else "**Timer:** Permanent"
        )
    except Exception as e:
        return await ask_channel_info.reply(f"**❌ Error:** `{e}`")
    
#===============================================================#

@Client.on_callback_query(filters.regex('^rm_fsub$'))
async def rm_fsub(client: Client, query: CallbackQuery):
    await query.answer()
    ask_channel_info = await client.ask(
        query.from_user.id, 
        "Send channel/group ID (negative integer) to remove in the next 60 seconds!", 
        filters=filters.text, 
        timeout=60
    )
    
    try:
        channel_id = int(ask_channel_info.text)
        if channel_id not in client.fsub_dict.keys():
            return await ask_channel_info.reply("**This channel/group is not in force sub list!**")
        
        # Check if it was a request channel and remove from req_channels
        if channel_id in client.req_channels:
            client.req_channels.remove(channel_id)
            await client.mongodb.set_channels(client.req_channels)
        
        # Remove from dict
        channel_name = client.fsub_dict[channel_id][0]
        client.fsub_dict.pop(channel_id)
        
        # Remove from database
        await client.mongodb.remove_fsub_channel(channel_id)
        
        await fsub(client, query)
        return await ask_channel_info.reply(
            f"**✅ Removed!**\n\n"
            f"**Name:** `{channel_name}`\n"
            f"**ID:** `{channel_id}`"
        )
    except Exception as e:
        return await ask_channel_info.reply(f"**❌ Error:** `{e}`")
