from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
from datetime import datetime
import asyncio

#===============================================================#

@Client.on_chat_join_request(filters.channel)
async def handle_join_request(client, join_request: ChatJoinRequest):
    """Enhanced join request handler with comprehensive tracking"""
    user_id = join_request.from_user.id
    channel_id = join_request.chat.id
    channel_name = join_request.chat.title
    channel = client.fsub_dict.get(channel_id, [])
    
    # Check if user is banned from the bot
    is_banned = await client.mongodb.is_banned(user_id)
    if is_banned:
        client.LOGGER(__name__, client.name).info(f"Blocked join request from banned user {user_id} for channel {channel_name}")
        return
    
    # Only process if this is a monitored force subscription channel
    if channel:
        try:
            # Ensure user exists in database
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id)
            
            # Record the join request with comprehensive data
            await client.mongodb.add_join_request(
                user_id, 
                channel_id, 
                getattr(join_request, 'id', None)
            )
            
            # Update fsub status to indicate request submitted
            await client.mongodb.update_fsub_status(user_id, channel_id, "request_submitted")
            
            # Add to channel users for compatibility
            await client.mongodb.add_channel_user(channel_id, user_id)
            
            client.LOGGER(__name__, client.name).info(
                f"Join request recorded: User {user_id} ({join_request.from_user.first_name}) → Channel {channel_name} ({channel_id})"
            )
            
            # Optional: Send notification to admins about new join request
            if hasattr(client, 'notify_admins_on_requests') and client.notify_admins_on_requests:
                await notify_admins_new_request(client, user_id, channel_id, channel_name, join_request.from_user)
                
        except Exception as e:
            client.LOGGER(__name__, client.name).error(f"Error handling join request for user {user_id} in channel {channel_name}: {e}")

#===============================================================#

@Client.on_chat_member_updated(filters.channel)
async def handle_member_update(client, chat_member_updated: ChatMemberUpdated):
    """Enhanced chat member update handler with comprehensive event tracking"""
    user_id = chat_member_updated.from_user.id
    channel_id = chat_member_updated.chat.id
    
    # Only process updates for monitored fsub channels
    if channel_id not in client.fsub_dict:
        return
    
    old_status = chat_member_updated.old_chat_member.status if chat_member_updated.old_chat_member else None
    new_status = chat_member_updated.new_chat_member.status if chat_member_updated.new_chat_member else None
    
    channel_name = client.fsub_dict[channel_id][0]
    user_name = chat_member_updated.from_user.first_name or "Unknown"
    
    try:
        # Ensure user exists in database
        if not await client.mongodb.present_user(user_id):
            await client.mongodb.add_user(user_id)
        
        # Handle different status transitions
        
        # User joined the channel (became member/admin/owner)
        if new_status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            await handle_user_joined(client, user_id, channel_id, channel_name, user_name, new_status)
            
        # User left the channel
        elif old_status == ChatMemberStatus.MEMBER:#in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER} and new_status == ChatMemberStatus.LEFT:
            await handle_user_left(client, user_id, channel_id, channel_name, user_name)
            
        # User was banned from the channel
        elif new_status == ChatMemberStatus.BANNED:
            await handle_user_banned(client, user_id, channel_id, channel_name, user_name)
            
        # User was restricted (limited permissions)
        elif new_status == ChatMemberStatus.RESTRICTED:
            await handle_user_restricted(client, user_id, channel_id, channel_name, user_name)
            
        # Handle role changes (member ↔ admin transitions)
        elif old_status != new_status and both_are_active_members(old_status, new_status):
            await handle_role_change(client, user_id, channel_id, channel_name, user_name, old_status, new_status)
            
    except Exception as e:
        client.LOGGER(__name__, client.name).error(
            f"Error handling member update for user {user_id} in channel {channel_name}: {e}"
        )

#===============================================================#

async def handle_user_joined(client, user_id, channel_id, channel_name, user_name, status):
    """Handle user joining the channel"""
    # Update database records
    await client.mongodb.update_fsub_status(user_id, channel_id, "joined")
    await client.mongodb.add_channel_user(channel_id, user_id)
    
    # If there was a pending join request, mark it as approved
    if await client.mongodb.has_submitted_join_request(user_id, channel_id):
        await client.mongodb.update_join_request_status(user_id, channel_id, "approved")
    
    # Log the event
    status_text = "as admin" if status == ChatMemberStatus.ADMINISTRATOR else "as member"
    client.LOGGER(__name__, client.name).info(
        f"✅ User {user_id} ({user_name}) joined channel {channel_name} {status_text}"
    )
    
    # Optional: Notify admins about new member
    if hasattr(client, 'notify_admins_on_joins') and client.notify_admins_on_joins:
        await notify_admins_user_joined(client, user_id, channel_id, channel_name, user_name)

async def handle_user_left(client, user_id, channel_id, channel_name, user_name):
    """Handle user leaving the channel"""
    # Update database records
    await client.mongodb.update_fsub_status(user_id, channel_id, "left")
    await client.mongodb.remove_channel_user(channel_id, user_id)
    
    # Clean up join request records
    if await client.mongodb.has_submitted_join_request(user_id, channel_id):
        await client.mongodb.remove_join_request(user_id, channel_id)
    
    # Log the event
    client.LOGGER(__name__, client.name).info(
        f"⬅️ User {user_id} ({user_name}) left channel {channel_name}"
    )
    
    # Optional: Notify admins about user leaving
    if hasattr(client, 'notify_admins_on_leaves') and client.notify_admins_on_leaves:
        await notify_admins_user_left(client, user_id, channel_id, channel_name, user_name)

async def handle_user_banned(client, user_id, channel_id, channel_name, user_name):
    """Handle user being banned from the channel"""
    # Update database records
    await client.mongodb.update_fsub_status(user_id, channel_id, "banned")
    await client.mongodb.remove_channel_user(channel_id, user_id)
    
    # Clean up join request records
    if await client.mongodb.has_submitted_join_request(user_id, channel_id):
        await client.mongodb.remove_join_request(user_id, channel_id)
    
    # Log the event
    client.LOGGER(__name__, client.name).warning(
        f"🚫 User {user_id} ({user_name}) was banned from channel {channel_name}"
    )
    
    # Optional: Notify admins about ban
    if hasattr(client, 'notify_admins_on_bans') and client.notify_admins_on_bans:
        await notify_admins_user_banned(client, user_id, channel_id, channel_name, user_name)

async def handle_user_restricted(client, user_id, channel_id, channel_name, user_name):
    """Handle user being restricted in the channel"""
    # Update database records (treat as limited member)
    await client.mongodb.update_fsub_status(user_id, channel_id, "restricted")
    await client.mongodb.add_channel_user(channel_id, user_id)  # Still count as member
    
    # Log the event
    client.LOGGER(__name__, client.name).info(
        f"⚠️ User {user_id} ({user_name}) was restricted in channel {channel_name}"
    )

async def handle_role_change(client, user_id, channel_id, channel_name, user_name, old_status, new_status):
    """Handle role changes between member and admin"""
    # Keep the user as joined since they're still in the channel
    await client.mongodb.update_fsub_status(user_id, channel_id, "joined")
    
    # Log the role change
    old_role = "admin" if old_status == ChatMemberStatus.ADMINISTRATOR else "member"
    new_role = "admin" if new_status == ChatMemberStatus.ADMINISTRATOR else "member"
    
    client.LOGGER(__name__, client.name).info(
        f"🔄 User {user_id} ({user_name}) role changed from {old_role} to {new_role} in channel {channel_name}"
    )

def both_are_active_members(old_status, new_status):
    """Check if both statuses represent active membership"""
    active_statuses = {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
    return old_status in active_statuses and new_status in active_statuses

#===============================================================#
# ADMIN NOTIFICATION FUNCTIONS
#===============================================================#

async def notify_admins_new_request(client, user_id, channel_id, channel_name, user):
    """Notify admins about new join requests"""
    try:
        message = f"🔔 **New Join Request**\n\n"
        message += f"👤 **User:** {user.first_name}"
        if user.username:
            message += f" (@{user.username})"
        message += f"\n🆔 **User ID:** `{user_id}`"
        message += f"\n📢 **Channel:** {channel_name}"
        message += f"\n🏷️ **Channel ID:** `{channel_id}`"
        
        for admin_id in client.admins:
            try:
                await client.send_message(admin_id, message)
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to notify admin {admin_id}: {e}")
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in notify_admins_new_request: {e}")

async def notify_admins_user_joined(client, user_id, channel_id, channel_name, user_name):
    """Notify admins when user joins"""
    # Implementation for join notifications
    pass

async def notify_admins_user_left(client, user_id, channel_id, channel_name, user_name):
    """Notify admins when user leaves"""
    # Implementation for leave notifications
    pass

async def notify_admins_user_banned(client, user_id, channel_id, channel_name, user_name):
    """Notify admins when user is banned"""
    # Implementation for ban notifications
    pass

#===============================================================#
# PERIODIC CLEANUP AND MAINTENANCE
#===============================================================#

async def setup_periodic_cleanup(client):
    """Setup periodic database cleanup tasks"""
    async def cleanup_task():
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await perform_database_cleanup(client)
            except Exception as e:
                client.LOGGER(__name__, client.name).error(f"Error in cleanup task: {e}")
    
    # Start the cleanup task in background
    asyncio.create_task(cleanup_task())

async def perform_database_cleanup(client):
    """Perform comprehensive database cleanup"""
    try:
        client.LOGGER(__name__, client.name).info("Starting periodic database cleanup...")
        
        # Clean expired fsub status records (older than 7 days)
        await client.mongodb.clear_expired_fsub_statuses(7)
        
        # Clean old join request records (older than 30 days)
        await client.mongodb.clear_old_join_requests(30)
        
        # Verify and clean invalid channel users
        await cleanup_invalid_channel_users(client)
        
        client.LOGGER(__name__, client.name).info("Database cleanup completed successfully")
        
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error during database cleanup: {e}")

async def cleanup_invalid_channel_users(client):
    """Remove users from channel database who are no longer members"""
    try:
        for channel_id in client.fsub_dict.keys():
            channel_users = await client.mongodb.get_channel_users(channel_id)
            
            for user_id in channel_users:
                try:
                    # Check if user is still a member
                    member = await client.get_chat_member(channel_id, user_id)
                    if member.status not in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                        # User is no longer a member, remove from database
                        await client.mongodb.remove_channel_user(channel_id, user_id)
                        await client.mongodb.update_fsub_status(user_id, channel_id, "left")
                        
                except Exception:
                    # User not found or error, remove from database
                    await client.mongodb.remove_channel_user(channel_id, user_id)
                    await client.mongodb.update_fsub_status(user_id, channel_id, "left")
                    
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error cleaning invalid channel users: {e}")
        
