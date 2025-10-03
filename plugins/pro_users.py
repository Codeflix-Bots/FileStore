#SahilxCodes

from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
from datetime import timedelta
import re
from config import OWNER_ID
#--------------------------------

def parse_duration(duration_str: str) -> timedelta:
    """
    Parse duration strings like '1 day', '2 weeks', '3 months', '1 year' into timedelta
    Returns None if the format is invalid
    """
    duration_str = duration_str.lower().strip()
    match = re.match(r'^(\d+)\s*(day|days|week|weeks|month|months|year|years)$', duration_str)
    
    if not match:
        return None
        
    amount = int(match.group(1))
    unit = match.group(2).rstrip('s')  # Remove 's' from plural forms
    
    if unit == 'day':
        return timedelta(days=amount)
    elif unit == 'week':
        return timedelta(weeks=amount)
    elif unit == 'month':
        return timedelta(days=amount * 30)  # Approximate
    elif unit == 'year':
        return timedelta(days=amount * 365)  # Approximate
    
    return None

#========================================================================#

@Client.on_message(filters.command('addpremium') & filters.private)
async def add_admin_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("Only Owner can use this command...!")

    usage = """<b>Usage:</b> 
/addpremium <userid> [duration]

<b>Examples:</b>
• /addpremium 123456 1 day
• /addpremium 123456 2 weeks
• /addpremium 123456 1 month
• /addpremium 123456 1 year
• /addpremium 123456 (for permanent premium)"""

    parts = message.command[1:]
    if not parts:
        return await message.reply_text(usage)

    try:
        user_id_to_add = int(parts[0])
    except ValueError:
        return await message.reply_text("Invalid user ID. Please check again...!")

    try:
        user = await client.get_users(user_id_to_add)
        user_name = user.first_name + (" " + user.last_name if user.last_name else "")
    except Exception as e:
        return await message.reply_text(f"Error fetching user information: {e}")

    # Parse duration if provided
    duration_str = " ".join(parts[1:]) if len(parts) > 1 else None
    expiry_date = None
    duration_text = "permanently"

    if duration_str:
        duration = parse_duration(duration_str)
        if not duration:
            return await message.reply_text(f"Invalid duration format. {usage}")
        expiry_date = datetime.now() + duration
        duration_text = f"until {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}"

    if not await client.mongodb.is_pro(user_id_to_add):
        await client.mongodb.add_pro(user_id_to_add, expiry_date)
        await message.reply_text(f"<b>User {user_name} - {user_id_to_add} is now a pro user {duration_text}!</b>")
        try:
            notify_msg = "<b>🎉 Congratulations! Your premium membership has been activated"
            notify_msg += f" until {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}</b>" if expiry_date else " permanently</b>"
            await client.send_message(user_id_to_add, notify_msg)
        except Exception as e:
            await message.reply_text(f"Failed to notify the user: {e}")
    else:
        current_expiry = await client.mongodb.get_expiry_date(user_id_to_add)
        if current_expiry:
            await message.reply_text(
                f"<b>User {user_name} - {user_id_to_add} is already a pro user "
                f"until {current_expiry.strftime('%Y-%m-%d %H:%M:%S')}.</b>"
            )
        else:
            await message.reply_text(f"<b>User {user_name} - {user_id_to_add} is already a permanent pro user.</b>")

#========================================================================#

@Client.on_message(filters.command('delpremium') & filters.private)
async def remove_admin_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("Only Owner can use this command...!")

    if len(message.command) != 2:
        return await message.reply_text("<b>You're using wrong format do like this:</b> /delpremium <userid>")

    try:
        user_id_to_remove = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid user ID. Please check again...!")

    try:
        user = await client.get_users(user_id_to_remove)
        user_name = user.first_name + (" " + user.last_name if user.last_name else "")
    except Exception as e:
        return await message.reply_text(f"Error fetching user information: {e}")

    if await client.mongodb.is_pro(user_id_to_remove):
        await client.mongodb.remove_pro(user_id_to_remove)
        await message.reply_text(f"<b>User {user_name} - {user_id_to_remove} has been removed from pro users...!</b>")
        try:
            await client.send_message(user_id_to_remove, "<b>You membership has been ended.\n\nTo renew the membership\nContact: @GetoPro.</b>")
        except Exception as e:
            await message.reply_text(f"Failed to notify the user: {e}")
    else:
        await message.reply_text(f"<b>User {user_name} - {user_id_to_remove} is not a pro user or was not found in the pro list.</b>")

#========================================================================#


@Client.on_message(filters.command('premiumusers') & filters.private)
async def admin_list_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("Only Owner can use this command...!")

    pro_user_ids = await client.mongodb.get_pros_list()
    formatted_admins = []

    for user_id in pro_user_ids:
        try:
            user = await client.get_users(user_id)
            full_name = user.first_name + (" " + user.last_name if user.last_name else "")
            username = f"@{user.username}" if user.username else "No Username"
            expiry_date = await client.mongodb.get_expiry_date(user_id)
            status = f"(Expires: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')})" if expiry_date else "(Permanent)"
            formatted_admins.append(f"{full_name} - {username} {status}")
        except Exception as e:
            continue

    if formatted_admins:
        await message.reply_text(
            "<b>📊 Premium Users List:</b>\n\n" + "\n".join(formatted_admins),
            disable_web_page_preview=True
        )
    else:
        await message.reply_text("<b>No premium users found.</b>")

