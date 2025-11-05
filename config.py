import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional, List, Tuple

# -------------------
# Basic Bot Settings
# -------------------
LOG_FILE_NAME = "bot.log"
PORT = os.environ.get("PORT", "5190")
OWNER_ID = 7725254712

MSG_EFFECT = 5046509860389126442

SHORT_URL = os.environ.get("SHORT_URL", "linkshortify.com")
SHORT_API = os.environ.get("SHORT_API", "")
SHORT_TUT = os.environ.get("SHORT_TUT", "https://t.me/How_to_Download_7x/26")

# -------------------
# Pyrogram / Session
# -------------------
SESSION = os.environ.get("SESSION", "yato")
TOKEN = os.environ.get("TOKEN", "8445680094:AAHxMsdfXEN1oRWd-VJtAVEI9aIbBNwX1Vs")
API_ID = int(os.environ.get("API_ID", "27914983"))
API_HASH = os.environ.get("API_HASH", "3ee76f526ada3e20c389ebc9e76c3a68")
WORKERS = int(os.environ.get("WORKERS", "5"))

# -------------------
# Database Settings
# -------------------
DB_URI = os.environ.get(
    "DB_URI",
    "mongodb+srv://test12:test@test.bhebzbi.mongodb.net/?appName=test",
)
DB_NAME = os.environ.get("DB_NAME", "test")

# -------------------
# FSUBS: optional force-subscription channels
# Bot won’t stop if invite cannot be exported
# -------------------
_raw_fsubs = os.environ.get("FSUBS")  # Optional override as JSON-like or CSV not supported automatically
FSUBS = [[]]
if _raw_fsubs:
    try:
        import ast
        parsed = ast.literal_eval(_raw_fsubs)
        if isinstance(parsed, list):
            FSUBS = parsed
    except Exception:
        pass

def _validate_fsubs(fsubs) -> List[List]:
    valid = []
    for entry in fsubs:
        try:
            cid = int(entry[0])
            req = bool(entry[1])
            timer = int(entry[2])
            valid.append([cid, req, timer])
        except Exception:
            continue
    return valid

FSUBS = _validate_fsubs(FSUBS)

# -------------------
# Database Channel (Primary)
# -------------------
DEFAULT_DB_CHANNEL = -1002845326087
_db_channel_env = os.environ.get("DB_CHANNEL")

try:
    if _db_channel_env is not None and str(_db_channel_env).strip() != "":
        DB_CHANNEL = int(_db_channel_env)
    else:
        DB_CHANNEL = int(os.environ.get("DB_CHANNEL", DEFAULT_DB_CHANNEL))
except Exception:
    DB_CHANNEL = DEFAULT_DB_CHANNEL

# -------------------
# Other settings
# -------------------
AUTO_DEL = int(os.environ.get("AUTO_DEL", 300))
ADMINS = [7725254712]
DISABLE_BTN = bool(os.environ.get("DISABLE_BTN", "True") == "True")
PROTECT = bool(os.environ.get("PROTECT", "True") == "True")

# -------------------
# Messages
# -------------------
MESSAGES = {
    "START": "<b>›› ʜᴇʏ!!, {first} ~ <blockquote>\n ɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.</blockquote></b>",
    "FSUB": "<b><blockquote>›› ʜᴇʏ ×</blockquote>\n  ʏᴏᴜʀ ғɪʟᴇ ɪs ʀᴇᴀᴅʏ ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғɪʟᴇs</b>",
    "ABOUT": "<b>›› ᴄʀᴇᴀᴛᴇᴅ ʙʏ: <a href='https://t.me/kanish_bodh'>Gigga</a> \n›› ᴏᴡɴᴇʀ: @The_lordz\n›› ʟᴀɴɢᴜᴀɢᴇ: <a href='https://docs.python.org/3/'>Pʏᴛʜᴏɴ 3</a> \n›› ʟɪʙʀᴀʀʏ: <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ ᴠ2</a></blockquote>",
    "REPLY": "<b>📨 sᴇɴᴅ ᴍᴇ ᴀɴʏ ғɪʟᴇ ᴛᴏ ɢᴇᴛ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ</b>",
    "SHORT_MSG": "<b>📊 ʜᴇʏ {first}, \n\n‼️ ɢᴇᴛ ᴀʟʟ ꜰɪʟᴇꜱ ɪɴ ᴀ ꜱɪɴɢʟᴇ ʟɪɴᴋ ‼️\n\n ⌯ ʏᴏᴜʀ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ, ᴋɪɴᴅʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴏᴘᴇɴ ʟɪɴᴋ ʙᴜᴛᴛᴏɴ..</b>",
    "START_PHOTO": "https://graph.org/tt-10-12-5",
    "FSUB_PHOTO": "https://graph.org/tt-10-12-5",
    "SHORT_PIC": "https://graph.org/tt-10-12-5",
    "SHORT": "https://graph.org/tt-10-12-5",
}

# -------------------
# Logger factory
# -------------------
def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
    
