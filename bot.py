#(©) Codeflix_Bots

from aiohttp import web
from plugins import web_server

from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import LOGGER, PORT, OWNER_ID, SHORT_URL, SHORT_API, SHORT_TUT
from helper import MongoDB

version = "v1.0.0"


class Bot(Client):
    def __init__(self, session, workers, db, fsub, token, admins, messages, auto_del, db_uri, db_name, api_id, api_hash, protect, disable_btn):
        super().__init__(
            name=session,
            api_hash=api_hash,
            api_id=api_id,
            plugins={
                "root": "plugins"
            },
            workers=workers,
            bot_token=token
        )
        self.LOGGER = LOGGER
        self.name = session
        self.db = db
        self.fsub = fsub
        self.owner = OWNER_ID
        self.fsub_dict = {}
        self.admins = admins + [OWNER_ID] if OWNER_ID not in admins else admins
        self.messages = messages
        self.auto_del = auto_del
        self.protect = protect
        self.req_fsub = {}
        self.disable_btn = disable_btn
        self.reply_text = messages.get('REPLY', 'Do not send any useless message in the bot.')
        self.mongodb = MongoDB(db_uri, db_name)
        self.req_channels = []
        self.db_channels = {}  # Initialize DB channels dictionary
        self.primary_db_channel = db  # Set initial primary DB channel
    
    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        
        # Load fsub channels from static config first
        if len(self.fsub) > 0:
            for channel in self.fsub:
                try:
                    chat = await self.get_chat(channel[0])
                    name = chat.title
                    link = None
                    if not channel[1]:
                        link = chat.invite_link
                    if not link and not channel[2]:
                        chat_link = await self.create_chat_invite_link(channel[0], creates_join_request=channel[1])
                        link = chat_link.invite_link
                    if not channel[1]:
                        self.fsub_dict[channel[0]] = [name, link, False, 0]
                    if channel[1]:
                        self.fsub_dict[channel[0]] = [name, link, True, 0]
                        self.req_channels.append(channel[0])
                    if channel[2] > 0:
                        self.fsub_dict[channel[0]] = [name, None, channel[1], channel[2]]
                except Exception as e:
                    self.LOGGER(__name__, self.name).warning("Bot can't Export Invite link from Force Sub Channel!")
                    self.LOGGER(__name__, self.name).warning("\nBot Stopped.")
                    sys.exit()
                    
        # Load dynamically added fsub channels from database
        try:
            db_fsub_channels = await self.mongodb.get_fsub_channels()
            for channel_id_str, channel_data in db_fsub_channels.items():
                channel_id = int(channel_id_str)
                # Skip if already loaded from static config
                if channel_id in self.fsub_dict:
                    continue
                try:
                    chat = await self.get_chat(channel_id)
                    name = chat.title
                    # Update name in case it changed
                    channel_data[0] = name
                    self.fsub_dict[channel_id] = channel_data
                    if channel_data[2]:  # if request is True
                        self.req_channels.append(channel_id)
                except Exception as e:
                    self.LOGGER(__name__, self.name).warning(f"Could not load dynamic fsub channel {channel_id}: {e}")
                    # Remove invalid channel from database
                    await self.mongodb.remove_fsub_channel(channel_id)
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(f"Error loading dynamic fsub channels: {e}")
            
        await self.mongodb.set_channels(self.req_channels)
        
        # Load DB channels from database
        try:
            db_channels_data = await self.mongodb.get_db_channels()
            self.db_channels = {}
            self.primary_db_channel = self.db
            
            for channel_id_str, channel_data in db_channels_data.items():
                channel_id = int(channel_id_str)
                try:
                    # Verify channel still exists and is accessible
                    chat = await self.get_chat(channel_id)
                    # Update name in case it changed
                    channel_data['name'] = chat.title
                    self.db_channels[channel_id_str] = channel_data
                    
                    # Set primary channel if marked as primary
                    if channel_data.get('is_primary', False):
                        self.primary_db_channel = channel_id
                        self.db = channel_id  # Update current db reference
                        
                except Exception as e:
                    self.LOGGER(__name__, self.name).warning(f"Could not load DB channel {channel_id}: {e}")
                    # Remove invalid channel from database
                    await self.mongodb.remove_db_channel(channel_id)
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(f"Error loading DB channels: {e}")
        
        # Load shortner settings from database
        try:
            shortner_settings = await self.mongodb.get_shortner_settings()
            self.short_url = shortner_settings.get('short_url', SHORT_URL)
            self.short_api = shortner_settings.get('short_api', SHORT_API)
            self.tutorial_link = shortner_settings.get('tutorial_link', SHORT_TUT)
            self.shortner_enabled = shortner_settings.get('enabled', True)
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(f"Error loading shortner settings: {e}")
            # Set defaults from config if loading fails
            self.short_url = SHORT_URL
            self.short_api = SHORT_API
            self.tutorial_link = SHORT_TUT
            self.shortner_enabled = True
        
        try:
            db_channel = await self.get_chat(self.db)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Testing Message by @ProYato")
            await test.delete()
            
            # Log DB channels info
            self.LOGGER(__name__, self.name).info(f"Primary DB Channel: {self.primary_db_channel}")
            self.LOGGER(__name__, self.name).info(f"Total DB Channels: {len(self.db_channels)}")
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(e)
            self.LOGGER(__name__, self.name).warning(f"Make Sure bot is Admin in DB Channel, and Double check the database channel Value, Current Value {self.db}")
            self.LOGGER(__name__, self.name).info("\nBot Stopped. Join https://t.me/animes_cruise for support")
            sys.exit()
        self.LOGGER(__name__, self.name).info("Bot Started!!")
        
        # Send restart msge to owner
        try:
            restart_message = "<b>›› ʜᴇʏ sᴇɴᴘᴀɪ!!\n ɪ'ᴍ ᴀʟɪᴠᴇ ɴᴏᴡ 🍃...</b>"
            await self.send_message(chat_id=self.owner, text=restart_message)
            self.LOGGER(__name__, self.name).info(f"Restart notification sent to owner: {self.owner}")
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(f"Failed to send restart notification to owner: {e}")
        
        self.username = usr_bot_me.username
    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__, self.name).info("Bot stopped.")


async def web_app():
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
