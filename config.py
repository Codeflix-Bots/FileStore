  # Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport


import os
from os import environ,getenv
import logging
from logging.handlers import RotatingFileHandler

#rohit_1888 on Tg

#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7542241757:")
#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", ""))
#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")
#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002170811388"))
# NAMA OWNER
OWNER = os.environ.get("OWNER", "sewxiy")
#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "7328629001"))
#Port
PORT = os.environ.get("PORT", "8030")
#Database
DB_URI = os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster0")

#Time in seconds for message delete, put 0 to never delete
TIME = int(os.environ.get("TIME", "600"))


#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL1 = int(os.environ.get("FORCE_SUB_CHANNEL1", "-1002215102799"))
#put 0 to disable
FORCE_SUB_CHANNEL2 = int(os.environ.get("FORCE_SUB_CHANNEL2", "0"))#put 0 to disable
FORCE_SUB_CHANNEL3 = int(os.environ.get("FORCE_SUB_CHANNEL3", "0"))#put 0 to disable
FORCE_SUB_CHANNEL4 = int(os.environ.get("FORCE_SUB_CHANNEL4", "0"))#put 0 to disable

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

START_PIC = os.environ.get("START_PIC", "https://w.wallhaven.cc/full/6d/wallhaven-6d9qpl.png")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://w.wallhaven.cc/full/gp/wallhaven-gpoovd.jpg")

# Turn this feature on or off using True or False put value inside  ""
# TRUE for yes FALSE if no 
TOKEN = True if os.environ.get('TOKEN', "False")
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "publicearn.online")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "adabe1c0675be8ffc5ccbc84a9a65bc5a5d3ec69")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 600)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID","https://t.me/hwdownload/3")


HELP_TXT = HELP_TXT = "<b><blockquote>ᴛʜɪs ɪs ᴀ ғɪʟᴇ ᴛᴏ ʟɪɴᴋ ʙᴏᴛ ᴡᴏʀᴋ ғᴏʀ @cypherixsocity\n\n❏ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs\n├ /start : sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n├ /about : ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛ\n└ /help : ɢᴇᴛ ʜᴇʟᴘ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ʙᴏᴛ\n\n 🔹 sɪᴍᴘʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʟɪɴᴋ, sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ, ᴊᴏɪɴ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ!\n\n 🔹 ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ <a href=https://t.me/cypherixsocity>ᴄʏᴘʜᴇʀɪx sᴏᴄɪᴛʏ</a></blockquote></b>"


ABOUT_TXT = ABOUT_TXT = "<b><blockquote>🚀 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <a href=https://t.me/cypherixsocity>ᴄʏᴘʜᴇʀɪx sᴏᴄɪᴛʏ</a> – ᴡʜᴇʀᴇ ᴡᴇ ᴛᴜʀɴ ᴄᴏғғᴇᴇ ɪɴᴛᴏ ᴄᴏᴅᴇ & ᴍᴇᴍᴇs ɪɴᴛᴏ ᴄᴏᴜʀsᴇs! ☕💻\n\n👨‍💻 ᴡʜᴀᴛ ᴡᴇ ᴅᴏ:\n✔ ᴡᴇʙ ᴅᴇᴠᴇʟᴏᴘᴍᴇɴᴛ 🖥️\n✔ ᴇᴅɪᴛɪɴɢ & ᴘʀᴏᴅᴜᴄᴛɪᴏɴ 🎬\n✔ ᴄʏʙᴇʀsᴇᴄᴜʀɪᴛʏ & ᴛᴇᴄʜ ꜰᴜɴ 🤖\n✔ ᴄᴏᴜʀsᴇs ᴛʜᴀᴛ ᴀᴄᴛᴜᴀʟʟʏ ᴍᴀᴋᴇ ʏᴏᴜ sᴏᴜɴᴅ sᴍᴀʀᴛ 😆\n\n🤣 ʜᴇʀᴇ’ꜱ ᴡʜʏ ʏᴏᴜ ꜱʜᴏᴜʟᴅ ᴊᴏɪɴ:\n❌ ᴡᴇ ᴅᴏɴ'ᴛ ᴘʀᴏᴍɪsᴇ ʏᴏᴜ'ʟʟ ʙᴇᴄᴏᴍᴇ ᴇʟᴏɴ ᴍᴜꜱᴋ...\n✅ ʙᴜᴛ ʏᴏᴜ ᴡɪʟʟ ʟᴇᴀʀɴ ᴄᴏᴅɪɴɢ, ᴄʏʙᴇʀsᴇᴄ, & ᴠɪᴅᴇᴏ ᴇᴅɪᴛɪɴɢ ᴡɪᴛʜ ᴄᴏᴏʟ ᴘᴇᴏᴘʟᴇ! 😎\n\n📢 ᴊᴏɪɴ ɴᴏᴡ, ᴏʀ ʀᴇɢʀᴇᴛ ɪᴛ ᴡʜᴇɴ ʏᴏᴜ’ʀᴇ ᴛʀʏɪɴɢ ᴛᴏ ɢᴏᴏɢʟᴇ “ʜᴏᴡ ᴛᴏ ᴍᴀᴋᴇ ᴀ ᴡᴇʙsɪᴛᴇ” ᴀᴛ 3ᴀᴍ! 😂</blockquote></b>"


START_MSG = os.environ.get("START_MESSAGE",
    "<b><blockquote>👋 ᴡᴇʟᴄᴏᴍᴇ, {first}...\n\n"
    "I'ᴍ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ ғɪʟᴇ ᴠᴇɴᴅɪɴɢ ᴍᴀᴄʜɪɴᴇ. ᴅʀᴏᴘ ᴀ ʟɪɴᴋ, ɢᴇᴛ ᴀ ғɪʟᴇ. \n"
    "ɴᴏ sᴍᴀʟʟ ᴛᴀʟᴋ—ɪ’ᴍ ɴᴏᴛ ʏᴏᴜʀ ᴇx! ❌😂\n\n"
    "🚀 ᴊᴏɪɴ ᴛʜᴇ ᴜɴᴅᴇʀɢʀᴏᴜɴᴅ: @cypherixsocity</blockquote></b>"
)
try:
    ADMINS=[6376328008]
    for x in (os.environ.get("ADMINS", "5115691197 6273945163 6103092779 5231212075").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {first}\n\n<b>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b>")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>• ʙʏ @OtakuFlix_Network</b>")

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"

ADMINS.append(OWNER_ID)
ADMINS.append(6497757690)

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
   
