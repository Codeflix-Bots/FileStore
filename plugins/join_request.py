from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus, ChatType

@Client.on_chat_join_request()  # ✅ Remove filters.channel to handle BOTH channels AND groups
async def handle_join_request(client, join_request: ChatJoinRequest):
    """Handle join request for fsub channels AND groups"""
    user_id = join_request.from_user.id
    channel_id = join_request.chat.id
    
    # Only process monitored fsub channels/groups
    if channel_id not in client.fsub_dict:
        return
        
    # Check if user is banned
    if await client.mongodb.is_banned(user_id):
        return
    
    try:
        # Ensure user exists in database
        if not await client.mongodb.present_user(user_id):
            await client.mongodb.add_user(user_id)
        
        # Record join request
        await client.mongodb.add_join_request(user_id, channel_id, getattr(join_request, 'id', None))
        await client.mongodb.update_fsub_status(user_id, channel_id, "request_submitted")
        await client.mongodb.add_channel_user(channel_id, user_id)
        
        client.LOGGER(__name__, client.name).info(f"Join request recorded: User {user_id} in chat {channel_id}")
        
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Join request error: {user_id} in {channel_id}: {e}")

@Client.on_chat_member_updated()  # ✅ Remove filters.channel to handle BOTH
async def handle_member_update(client, chat_member_updated: ChatMemberUpdated):
    """Handle member status updates for fsub channels AND groups"""
    user_id = chat_member_updated.from_user.id
    channel_id = chat_member_updated.chat.id
    
    # Only process monitored fsub channels/groups
    if channel_id not in client.fsub_dict:
        return
    
    old_status = chat_member_updated.old_chat_member.status if chat_member_updated.old_chat_member else None
    new_status = chat_member_updated.new_chat_member.status if chat_member_updated.new_chat_member else None
    
    try:
        # Ensure user exists
        if not await client.mongodb.present_user(user_id):
            await client.mongodb.add_user(user_id)
        
        # Handle status changes properly
        active_statuses = {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
        
        # User joined - old_status is None/inactive, new_status is active
        if new_status in active_statuses and (old_status is None or old_status not in active_statuses):
            await client.mongodb.update_fsub_status(user_id, channel_id, "joined")
            await client.mongodb.add_channel_user(channel_id, user_id)
            
            # Mark join request as approved if exists
            if await client.mongodb.has_submitted_join_request(user_id, channel_id):
                await client.mongodb.update_join_request_status(user_id, channel_id, "approved")
            
            client.LOGGER(__name__, client.name).info(f"User {user_id} joined chat {channel_id}")
                
        # User left/banned - old_status is active, new_status is None/inactive
        elif old_status in active_statuses and (new_status is None or new_status not in active_statuses):
            await client.mongodb.update_fsub_status(user_id, channel_id, "left")
            await client.mongodb.remove_channel_user(channel_id, user_id)
            
            # Clean up join request
            if await client.mongodb.has_submitted_join_request(user_id, channel_id):
                await client.mongodb.remove_join_request(user_id, channel_id)
            
            client.LOGGER(__name__, client.name).info(f"User {user_id} left chat {channel_id}")
                
        # Handle specific banned status
        elif new_status == ChatMemberStatus.BANNED:
            await client.mongodb.update_fsub_status(user_id, channel_id, "banned")
            await client.mongodb.remove_channel_user(channel_id, user_id)
            
            # Clean up join request
            if await client.mongodb.has_submitted_join_request(user_id, channel_id):
                await client.mongodb.remove_join_request(user_id, channel_id)
            
            client.LOGGER(__name__, client.name).info(f"User {user_id} banned from chat {channel_id}")
                
        # Handle restricted status
        elif new_status == ChatMemberStatus.RESTRICTED:
            await client.mongodb.update_fsub_status(user_id, channel_id, "restricted")
            await client.mongodb.add_channel_user(channel_id, user_id)
            
            client.LOGGER(__name__, client.name).info(f"User {user_id} restricted in chat {channel_id}")
            
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Member update error: {user_id} in {channel_id}: {e}")
