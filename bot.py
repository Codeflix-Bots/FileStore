#(©)Codexbotz @Codeflix_Bots

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCESUB_CHANNEL, FORCESUB_CHANNEL2, FORCESUB_CHANNEL3, CHANNEL_ID, PORT

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCESUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCESUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCESUB_CHANNEL)
                    link = (await self.get_chat(FORCESUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCESUB_CHANNEL value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCESUB_CHANNEL}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
                sys.exit()
        if FORCESUB_CHANNEL2:
            try:
                link = (await self.get_chat(FORCESUB_CHANNEL2)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCESUB_CHANNEL2)
                    link = (await self.get_chat(FORCESUB_CHANNEL2)).invite_link
                self.invitelink2 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCESUB_CHANNEL2 value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCESUB_CHANNEL2}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
                sys.exit()
        if FORCESUB_CHANNEL3:
            try:
                link = (await self.get_chat(FORCESUB_CHANNEL3)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCESUB_CHANNEL3)
                    link = (await self.get_chat(FORCESUB_CHANNEL3)).invite_link
                self.invitelink3 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCESUB_CHANNEL3 value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCESUB_CHANNEL3}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
                sys.exit()       
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/Animes_X_Hunters")
        self.LOGGER(__name__).info(f""" \n\n       

  _____ ____  _____  ______ ______ _      _______   ______   ____ _______ _____ 
 / ____/ __ \|  __ \|  ____|  ____| |    |_   _\ \ / /  _ \ / __ \__   __/ ____|
| |   | |  | | |  | | |__  | |__  | |      | |  \ V /| |_) | |  | | | | | (___  
| |   | |  | | |  | |  __| |  __| | |      | |   > < |  _ <| |  | | | |  \___ \ 
| |___| |__| | |__| | |____| |    | |____ _| |_ / . \| |_) | |__| | | |  ____) |
 \_____\____/|_____/|______|_|    |______|_____/_/ \_\____/ \____/  |_| |_____/ 
                                                                                
                                                                                
                                          """)
        self.username = usr_bot_me.username
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
