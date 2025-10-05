import motor.motor_asyncio
from datetime import datetime, timedelta

class MongoDB:
    _instances = {}

    def __new__(cls, uri: str, db_name: str):
        if (uri, db_name) not in cls._instances:
            instance = super().__new__(cls)
            instance.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            instance.db = instance.client[db_name]
            instance.user_data = instance.db["users"]
            instance.channel_data = instance.db["channels"]
            instance.premium_users = instance.db['pros']
            instance.fsub_status = instance.db['fsub_status']  # New collection for fsub status tracking
            instance.request_sub = instance.db['request_sub']  # New collection for join request tracking
            cls._instances[(uri, db_name)] = instance
        return cls._instances[(uri, db_name)]

    async def set_channels(self, channels: list[int]):
        await self.user_data.update_one(
            {"_id": 1},
            {"$set": {"channels": channels}},
            upsert=True
        )

    async def get_channels(self) -> list[int]:
        data = await self.user_data.find_one({"_id": 1})
        return data.get("channels", []) if data else []

    async def add_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one(
            {"_id": channel_id},
            {"$addToSet": {"users": user_id}},
            upsert=True
        )

    async def remove_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one(
            {"_id": channel_id},
            {"$pull": {"users": user_id}}
        )

    async def get_channel_users(self, channel_id: int) -> list[int]:
        doc = await self.channel_data.find_one({"_id": channel_id})
        return doc.get("users", []) if doc else []

    async def is_user_in_channel(self, channel_id: int, user_id: int) -> bool:
        doc = await self.channel_data.find_one(
            {"_id": channel_id, "users": {"$in": [user_id]}},
            {"_id": 1}
        )
        return doc is not None

    # ✅ PRO FEATURES

    async def add_pro(self, user_id: int, expiry_date: datetime = None):
        try:
            await self.premium_users.update_one(
                {'_id': user_id},
                {'$set': {'expiry_date': expiry_date}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Failed to add premium user: {e}")
            return False

    async def remove_pro(self, user_id: int):
        try:
            await self.premium_users.delete_one({'_id': user_id})
            return True
        except Exception as e:
            print(f"Failed to remove premium user: {e}")
            return False

    async def is_pro(self, user_id: int):
        doc = await self.premium_users.find_one({'_id': user_id})
        if not doc:
            return False
        if 'expiry_date' not in doc:
            return True  # Legacy premium users without expiry date
        if doc['expiry_date'] is None:
            return True  # Permanent premium users
        return doc['expiry_date'] > datetime.now()

    async def get_pros_list(self):
        current_time = datetime.now()
        cursor = self.premium_users.find({
            '$or': [
                {'expiry_date': None},  # Permanent premium users
                {'expiry_date': {'$exists': False}},  # Legacy premium users
                {'expiry_date': {'$gt': current_time}}  # Active premium users
            ]
        })
        return [doc['_id'] async for doc in cursor]
        
    async def get_expiry_date(self, user_id: int) -> datetime:
        doc = await self.premium_users.find_one({'_id': user_id})
        return doc.get('expiry_date') if doc else None

    # ✅ USER FUNCTIONS

    async def present_user(self, user_id: int) -> bool:
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int, ban: bool = False):
        await self.user_data.insert_one({'_id': user_id, 'ban': ban})

    async def full_userbase(self) -> list[int]:
        cursor = self.user_data.find()
        return [doc['_id'] async for doc in cursor]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})

    async def ban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': True}})

    async def unban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': False}})

    async def is_banned(self, user_id: int) -> bool:
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('ban', False) if user else False

    # ✅ FSUB CHANNELS FUNCTIONS

    async def set_fsub_channels(self, fsub_data: dict):
        """Store fsub channels data to database for persistence across bot restarts"""
        await self.user_data.update_one(
            {"_id": "fsub_channels"},
            {"$set": {"channels": fsub_data}},
            upsert=True
        )

    async def get_fsub_channels(self) -> dict:
        """Get fsub channels data from database"""
        data = await self.user_data.find_one({"_id": "fsub_channels"})
        return data.get("channels", {}) if data else {}

    async def add_fsub_channel(self, channel_id: int, channel_data: list):
        """Add a single fsub channel to database"""
        current_data = await self.get_fsub_channels()
        current_data[str(channel_id)] = channel_data
        await self.set_fsub_channels(current_data)

    async def remove_fsub_channel(self, channel_id: int):
        """Remove a single fsub channel from database"""
        current_data = await self.get_fsub_channels()
        current_data.pop(str(channel_id), None)
        await self.set_fsub_channels(current_data)

    # ✅ SHORTNER SETTINGS FUNCTIONS

    async def set_shortner_settings(self, shortner_data: dict):
        """Store shortner settings to database for persistence across bot restarts"""
        await self.user_data.update_one(
            {"_id": "shortner_settings"},
            {"$set": {"settings": shortner_data}},
            upsert=True
        )

    async def get_shortner_settings(self) -> dict:
        """Get shortner settings from database"""
        data = await self.user_data.find_one({"_id": "shortner_settings"})
        return data.get("settings", {}) if data else {}

    async def update_shortner_setting(self, key: str, value: str):
        """Update a single shortner setting"""
        current_data = await self.get_shortner_settings()
        current_data[key] = value
        await self.set_shortner_settings(current_data)

    async def get_shortner_status(self) -> bool:
        """Get shortner on/off status"""
        settings = await self.get_shortner_settings()
        return settings.get('enabled', True)  # Default is enabled

    async def set_shortner_status(self, enabled: bool):
        """Set shortner on/off status"""
        await self.update_shortner_setting('enabled', enabled)

    # ✅ FSUB STATUS COLLECTION FUNCTIONS

    async def update_fsub_status(self, user_id: int, channel_id: int, status: str):
        """Update user's subscription status for a specific channel"""
        await self.fsub_status.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {"status": status, "last_updated": datetime.now()}},
            upsert=True
        )

    async def get_fsub_status(self, user_id: int, channel_id: int) -> str:
        """Get user's subscription status for a specific channel"""
        doc = await self.fsub_status.find_one({"user_id": user_id, "channel_id": channel_id})
        return doc.get("status") if doc else None

    async def remove_fsub_status(self, user_id: int, channel_id: int):
        """Remove user's fsub status record"""
        await self.fsub_status.delete_one({"user_id": user_id, "channel_id": channel_id})

    async def get_user_fsub_statuses(self, user_id: int) -> dict:
        """Get all fsub statuses for a user"""
        cursor = self.fsub_status.find({"user_id": user_id})
        statuses = {}
        async for doc in cursor:
            statuses[doc["channel_id"]] = doc["status"]
        return statuses

    async def clear_expired_fsub_statuses(self, days: int = 7):
        """Clear fsub status records older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        await self.fsub_status.delete_many({"last_updated": {"$lt": cutoff_date}})

    # ✅ REQUEST SUB COLLECTION FUNCTIONS

    async def add_join_request(self, user_id: int, channel_id: int, request_id: int = None):
        """Record a join request submission"""
        await self.request_sub.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {
                "request_id": request_id,
                "status": "pending",
                "submitted_at": datetime.now(),
                "last_updated": datetime.now()
            }},
            upsert=True
        )

    async def update_join_request_status(self, user_id: int, channel_id: int, status: str):
        """Update join request status (pending, approved, rejected)"""
        await self.request_sub.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {"status": status, "last_updated": datetime.now()}}
        )

    async def get_join_request_status(self, user_id: int, channel_id: int) -> str:
        """Get join request status"""
        doc = await self.request_sub.find_one({"user_id": user_id, "channel_id": channel_id})
        return doc.get("status") if doc else None

    async def has_submitted_join_request(self, user_id: int, channel_id: int) -> bool:
        """Check if user has submitted a join request for channel"""
        doc = await self.request_sub.find_one({"user_id": user_id, "channel_id": channel_id})
        return doc is not None

    async def remove_join_request(self, user_id: int, channel_id: int):
        """Remove join request record"""
        await self.request_sub.delete_one({"user_id": user_id, "channel_id": channel_id})

    async def get_pending_requests_for_channel(self, channel_id: int) -> list:
        """Get all pending join requests for a channel"""
        cursor = self.request_sub.find({"channel_id": channel_id, "status": "pending"})
        requests = []
        async for doc in cursor:
            requests.append({
                "user_id": doc["user_id"],
                "request_id": doc.get("request_id"),
                "submitted_at": doc["submitted_at"]
            })
        return requests

    async def clear_old_join_requests(self, days: int = 30):
        """Clear join request records older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        await self.request_sub.delete_many({"submitted_at": {"$lt": cutoff_date}})

    async def cleanup_database(self):
        """Perform comprehensive database maintenance - clean old records and validate data"""
        try:
            # Clean old fsub status records (older than 7 days)
            await self.clear_expired_fsub_statuses(7)
            # Clean old join request records (older than 30 days)
            await self.clear_old_join_requests(30)
            
            # Additional cleanup for orphaned records
            await self.cleanup_orphaned_records()
            
            return True
        except Exception as e:
            print(f"Database cleanup error: {e}")
            return False

    async def cleanup_orphaned_records(self):
        """Clean up records that are no longer valid"""
        try:
            # Remove fsub status records for users who no longer exist
            users = await self.full_userbase()
            user_ids_set = set(users)
            
            # Clean fsub_status collection
            async for doc in self.fsub_status.find({"user_id": {"$nin": users}}):
                await self.fsub_status.delete_one({"_id": doc["_id"]})
            
            # Clean request_sub collection
            async for doc in self.request_sub.find({"user_id": {"$nin": users}}):
                await self.request_sub.delete_one({"_id": doc["_id"]})
                
            return True
        except Exception as e:
            print(f"Error cleaning orphaned records: {e}")
            return False

    async def get_comprehensive_fsub_statistics(self):
        """Get detailed statistics about fsub system"""
        try:
            # Basic counts
            fsub_count = await self.fsub_status.count_documents({})
            request_count = await self.request_sub.count_documents({})
            pending_requests = await self.request_sub.count_documents({"status": "pending"})
            approved_requests = await self.request_sub.count_documents({"status": "approved"})
            rejected_requests = await self.request_sub.count_documents({"status": "rejected"})
            
            # Status breakdown
            status_breakdown = {}
            async for doc in self.fsub_status.aggregate([
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]):
                status_breakdown[doc["_id"]] = doc["count"]
            
            # Channel-wise statistics
            channel_stats = {}
            async for doc in self.fsub_status.aggregate([
                {"$group": {"_id": "$channel_id", "count": {"$sum": 1}}}
            ]):
                channel_stats[doc["_id"]] = doc["count"]
            
            # Recent activity (last 24 hours)
            from datetime import datetime, timedelta
            yesterday = datetime.now() - timedelta(days=1)
            recent_fsub_updates = await self.fsub_status.count_documents(
                {"last_updated": {"$gte": yesterday}}
            )
            recent_requests = await self.request_sub.count_documents(
                {"submitted_at": {"$gte": yesterday}}
            )
            
            return {
                "total_fsub_records": fsub_count,
                "total_join_requests": request_count,
                "pending_requests": pending_requests,
                "approved_requests": approved_requests,
                "rejected_requests": rejected_requests,
                "status_breakdown": status_breakdown,
                "channel_statistics": channel_stats,
                "recent_activity": {
                    "fsub_updates_24h": recent_fsub_updates,
                    "join_requests_24h": recent_requests
                }
            }
        except Exception as e:
            print(f"Error getting comprehensive fsub statistics: {e}")
            return {}

    async def get_user_activity_summary(self, user_id: int):
        """Get comprehensive activity summary for a specific user"""
        try:
            # Get all fsub statuses
            fsub_statuses = await self.get_user_fsub_statuses(user_id)
            
            # Get join request history
            join_requests = []
            async for doc in self.request_sub.find({"user_id": user_id}):
                join_requests.append({
                    "channel_id": doc["channel_id"],
                    "status": doc["status"],
                    "submitted_at": doc["submitted_at"],
                    "last_updated": doc["last_updated"]
                })
            
            # Check if user is banned
            is_banned = await self.is_banned(user_id)
            
            # Check if user is premium
            is_premium = await self.is_pro(user_id)
            
            return {
                "user_id": user_id,
                "is_banned": is_banned,
                "is_premium": is_premium,
                "fsub_statuses": fsub_statuses,
                "join_request_history": join_requests,
                "total_channels_joined": len([s for s in fsub_statuses.values() if s == "joined"]),
                "total_requests_submitted": len(join_requests)
            }
        except Exception as e:
            print(f"Error getting user activity summary for {user_id}: {e}")
            return {}

    async def get_channel_activity_summary(self, channel_id: int):
        """Get comprehensive activity summary for a specific channel"""
        try:
            # Get all users in channel
            channel_users = await self.get_channel_users(channel_id)
            
            # Get fsub status breakdown for this channel
            status_counts = {}
            async for doc in self.fsub_status.aggregate([
                {"$match": {"channel_id": channel_id}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]):
                status_counts[doc["_id"]] = doc["count"]
            
            # Get join request stats for this channel
            request_stats = {}
            async for doc in self.request_sub.aggregate([
                {"$match": {"channel_id": channel_id}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]):
                request_stats[doc["_id"]] = doc["count"]
            
            # Get recent activity (last 7 days)
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            recent_joins = await self.fsub_status.count_documents({
                "channel_id": channel_id,
                "status": "joined",
                "last_updated": {"$gte": week_ago}
            })
            
            recent_requests = await self.request_sub.count_documents({
                "channel_id": channel_id,
                "submitted_at": {"$gte": week_ago}
            })
            
            return {
                "channel_id": channel_id,
                "total_users": len(channel_users),
                "status_breakdown": status_counts,
                "request_statistics": request_stats,
                "recent_activity_7d": {
                    "new_joins": recent_joins,
                    "new_requests": recent_requests
                }
            }
        except Exception as e:
            print(f"Error getting channel activity summary for {channel_id}: {e}")
            return {}

    async def bulk_update_user_statuses(self, updates: list):
        """Perform bulk updates for user statuses - useful for synchronization"""
        try:
            operations = []
            for update in updates:
                user_id = update["user_id"]
                channel_id = update["channel_id"]
                status = update["status"]
                
                operations.append({
                    "updateOne": {
                        "filter": {"user_id": user_id, "channel_id": channel_id},
                        "update": {
                            "$set": {
                                "status": status,
                                "last_updated": datetime.now()
                            }
                        },
                        "upsert": True
                    }
                })
            
            if operations:
                result = await self.fsub_status.bulk_write(operations)
                return result
            return None
        except Exception as e:
            print(f"Error in bulk update user statuses: {e}")
            return None

    async def sync_channel_members(self, channel_id: int, current_members: list):
        """Synchronize database with actual channel members"""
        try:
            # Get stored users for this channel
            stored_users = await self.get_channel_users(channel_id)
            
            # Find users to add (in channel but not in database)
            users_to_add = set(current_members) - set(stored_users)
            
            # Find users to remove (in database but not in channel)
            users_to_remove = set(stored_users) - set(current_members)
            
            # Add new users
            for user_id in users_to_add:
                await self.add_channel_user(channel_id, user_id)
                await self.update_fsub_status(user_id, channel_id, "joined")
            
            # Remove old users
            for user_id in users_to_remove:
                await self.remove_channel_user(channel_id, user_id)
                await self.update_fsub_status(user_id, channel_id, "left")
            
            return {
                "added": len(users_to_add),
                "removed": len(users_to_remove),
                "synced": True
            }
        except Exception as e:
            print(f"Error syncing channel members for {channel_id}: {e}")
            return {"synced": False, "error": str(e)}

    async def export_fsub_data(self, channel_id: int = None):
        """Export force subscription data for backup or analysis"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "fsub_statuses": [],
                "join_requests": []
            }
            
            # Filter by channel if specified
            filter_query = {"channel_id": channel_id} if channel_id else {}
            
            # Export fsub statuses
            async for doc in self.fsub_status.find(filter_query):
                doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
                if "last_updated" in doc:
                    doc["last_updated"] = doc["last_updated"].isoformat()
                export_data["fsub_statuses"].append(doc)
            
            # Export join requests
            async for doc in self.request_sub.find(filter_query):
                doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
                if "submitted_at" in doc:
                    doc["submitted_at"] = doc["submitted_at"].isoformat()
                if "last_updated" in doc:
                    doc["last_updated"] = doc["last_updated"].isoformat()
                export_data["join_requests"].append(doc)
            
            return export_data
        except Exception as e:
            print(f"Error exporting fsub data: {e}")
            return None

    async def get_fsub_statistics(self):
        """Get statistics about fsub collections"""
        try:
            fsub_count = await self.fsub_status.count_documents({})
            request_count = await self.request_sub.count_documents({})
            pending_requests = await self.request_sub.count_documents({"status": "pending"})
            
            return {
                "fsub_status_records": fsub_count,
                "join_request_records": request_count,
                "pending_requests": pending_requests
            }
        except Exception as e:
            print(f"Error getting fsub statistics: {e}")
            return {}

    # ✅ DB CHANNELS FUNCTIONS

    async def set_db_channels(self, db_channels_data: dict):
        """Store DB channels data to database for persistence across bot restarts"""
        await self.user_data.update_one(
            {"_id": "db_channels"},
            {"$set": {"channels": db_channels_data}},
            upsert=True
        )

    async def get_db_channels(self) -> dict:
        """Get DB channels data from database"""
        data = await self.user_data.find_one({"_id": "db_channels"})
        return data.get("channels", {}) if data else {}

    async def add_db_channel(self, channel_id: int, channel_data: dict):
        """Add a single DB channel to database"""
        current_data = await self.get_db_channels()
        current_data[str(channel_id)] = channel_data
        await self.set_db_channels(current_data)

    async def remove_db_channel(self, channel_id: int):
        """Remove a single DB channel from database"""
        current_data = await self.get_db_channels()
        current_data.pop(str(channel_id), None)
        await self.set_db_channels(current_data)

    async def update_db_channel(self, channel_id: int, channel_data: dict):
        """Update a single DB channel in database"""
        current_data = await self.get_db_channels()
        if str(channel_id) in current_data:
            current_data[str(channel_id)].update(channel_data)
            await self.set_db_channels(current_data)

    async def get_primary_db_channel(self) -> int:
        """Get the primary DB channel ID"""
        db_channels = await self.get_db_channels()
        for channel_id_str, channel_data in db_channels.items():
            if channel_data.get('is_primary', False):
                return int(channel_id_str)
        return None

    async def set_primary_db_channel(self, channel_id: int):
        """Set a DB channel as primary (remove primary from others)"""
        db_channels = await self.get_db_channels()
        # Remove primary status from all channels
        for ch_id, ch_data in db_channels.items():
            ch_data['is_primary'] = False
        # Set new primary channel
        if str(channel_id) in db_channels:
            db_channels[str(channel_id)]['is_primary'] = True
        await self.set_db_channels(db_channels)

    async def get_active_db_channels(self) -> dict:
        """Get all active DB channels"""
        db_channels = await self.get_db_channels()
        active_channels = {}
        for channel_id_str, channel_data in db_channels.items():
            if channel_data.get('is_active', True):
                active_channels[channel_id_str] = channel_data
        return active_channels

    async def toggle_db_channel_status(self, channel_id: int):
        """Toggle DB channel active/inactive status"""
        db_channels = await self.get_db_channels()
        if str(channel_id) in db_channels:
            current_status = db_channels[str(channel_id)].get('is_active', True)
            db_channels[str(channel_id)]['is_active'] = not current_status
            await self.set_db_channels(db_channels)
            return not current_status
        return None

    # ✅ BOT SETTINGS FUNCTIONS

    async def set_bot_settings(self, settings_data: dict):
        """Store bot settings to database for persistence across bot restarts"""
        await self.user_data.update_one(
            {"_id": "bot_settings"},
            {"$set": {"settings": settings_data}},
            upsert=True
        )

    async def get_bot_settings(self) -> dict:
        """Get bot settings from database"""
        data = await self.user_data.find_one({"_id": "bot_settings"})
        return data.get("settings", {}) if data else {}

    async def update_bot_setting(self, key: str, value):
        """Update a single bot setting"""
        current_data = await self.get_bot_settings()
        current_data[key] = value
        await self.set_bot_settings(current_data)

    async def get_bot_setting(self, key: str, default=None):
        """Get a single bot setting with default fallback"""
        settings = await self.get_bot_settings()
        return settings.get(key, default)

    # ✅ MESSAGES SETTINGS FUNCTIONS

    async def set_messages_settings(self, messages_data: dict):
        """Store messages settings to database for persistence across bot restarts"""
        await self.user_data.update_one(
            {"_id": "messages_settings"},
            {"$set": {"messages": messages_data}},
            upsert=True
        )

    async def get_messages_settings(self) -> dict:
        """Get messages settings from database"""
        data = await self.user_data.find_one({"_id": "messages_settings"})
        return data.get("messages", {}) if data else {}

    async def update_message_setting(self, key: str, value: str):
        """Update a single message setting"""
        current_data = await self.get_messages_settings()
        current_data[key] = value
        await self.set_messages_settings(current_data)

    async def get_message_setting(self, key: str, default: str = ""):
        """Get a single message setting with default fallback"""
        messages = await self.get_messages_settings()
        return messages.get(key, default)

    # ✅ ADMIN SETTINGS FUNCTIONS

    async def set_admins_list(self, admins_list: list):
        """Store admins list to database for persistence across bot restarts"""
        await self.user_data.update_one(
            {"_id": "admins_list"},
            {"$set": {"admins": admins_list}},
            upsert=True
        )

    async def get_admins_list(self) -> list:
        """Get admins list from database"""
        data = await self.user_data.find_one({"_id": "admins_list"})
        return data.get("admins", []) if data else []

    async def add_admin(self, admin_id: int):
        """Add an admin to the database"""
        current_admins = await self.get_admins_list()
        if admin_id not in current_admins:
            current_admins.append(admin_id)
            await self.set_admins_list(current_admins)
            return True
        return False

    async def remove_admin(self, admin_id: int):
        """Remove an admin from the database"""
        current_admins = await self.get_admins_list()
        if admin_id in current_admins:
            current_admins.remove(admin_id)
            await self.set_admins_list(current_admins)
            return True
        return False

    # ✅ BATCH SETTINGS FUNCTIONS

    async def save_all_settings(self, bot_settings: dict, messages: dict, admins: list):
        """Save all settings in a single transaction for efficiency"""
        try:
            await self.set_bot_settings(bot_settings)
            await self.set_messages_settings(messages)
            await self.set_admins_list(admins)
            return True
        except Exception as e:
            print(f"Error saving all settings: {e}")
            return False

    async def load_all_settings(self) -> dict:
        """Load all settings in a single call for efficiency"""
        try:
            bot_settings = await self.get_bot_settings()
            messages = await self.get_messages_settings()
            admins = await self.get_admins_list()
            shortner_settings = await self.get_shortner_settings()
            
            return {
                "bot_settings": bot_settings,
                "messages": messages,
                "admins": admins,
                "shortner_settings": shortner_settings
            }
        except Exception as e:
            print(f"Error loading all settings: {e}")
            return {
                "bot_settings": {},
                "messages": {},
                "admins": [],
                "shortner_settings": {}
            }
