#(©)Codexbotz

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b>○ ᴏᴡɴᴇʀ : <a href='tg://user?id={OWNER_ID}'>STK OWNER</a>\n○ ᴍʏ ᴜᴘᴅᴀᴛᴇs : <a href='https://t.me/ssc_helpful_contents'>SSC BEST CHENNAL</a>\n○ SSC ALL PYQS : <a href='https://t.me/ssc_pyq'>ONE STOP SOLUTION</a>\n○ ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ : <a href='https://t.me/ssc_helpful_contents'>BEST CHENNAL</a>\n○ ALL MOVIES / WEBSERIES : <a href='https://t.me/stkmovies'>Relax Zone🍿🎬</a></b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("⚡️ ᴄʟᴏsᴇ", callback_data = "close"),
                    InlineKeyboardButton('🍁 𝐌𝐎𝐕𝐈𝐄 IN 𝐒𝐄𝐂𝐎𝐍𝐃𝐒', url='https://t.me/stkmoviehub')
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
