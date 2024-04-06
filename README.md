# ᴍᴜʟᴛɪ ғsᴜʙ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ ᴍᴏᴅɪғɪᴇᴅ ʙʏ ᴄᴏᴅᴇғʟɪx ʙᴏᴛs
<p align="center">
  <img src="https://graph.org/file/04206ec6d9b1606fdc107.jpg" alt="Multi FSub File Store by codeflix bots">
</p>
<h2 align="center">

<p align="center">


ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴛᴏ sᴛᴏʀᴇ ᴘᴏsᴛs ᴀɴᴅ ᴅᴏᴄᴜᴍᴇɴᴛs ᴀɴᴅ ɪᴛ ᴄᴀɴ ᴀᴄᴄᴇss ʙʏ sᴘᴇᴄɪᴀʟ ʟɪɴᴋs. ɪ ɢᴜᴇss ᴛʜɪs ᴡɪʟʟ ʙᴇ ᴜsᴇғᴜʟʟ ғᴏʀ ᴍᴀɴʏ ᴘᴇᴏᴘʟᴇ.....😇. 

##

**If you need any more modes in repo or If you find out any bugs, mention in <b>[sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ](https://github.com/weebs_support)  ➻  [ᴍɪᴋᴇʏ](https://t.me/sewxiy) </b>**


### Features
- Fully customisable.
- Customisable welcome & Forcesub messages.
- More than one Posts in One Link.
- Can be deployed on heroku directly.

### Setup

- Add the bot to Database Channel with all permission
- Add bot to ForceSub channel as Admin with Invite Users via Link Permission if you enabled ForceSub 

<details>
<summary><h3>
- <b> ᴅᴇᴘʟᴏʏᴍᴇɴᴛ ᴍᴇᴛʜᴏᴅs </b>
</h3></summary>
<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ 」─
</h3>

<p align="center"><a href="https://heroku.com/deploy?template=https://github.com/Codeflix-Bots/FileStore/tree/multi-fsub">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy On Heroku">
</a></p>
<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ᴋᴏʏᴇʙ 」─
</h3>
<p align="center"><a href="https://app.koyeb.com/deploy?type=git&repository=github.com/Codeflix-Bots/FileStore&branch=multi-fsub&name=multi-fsub">
  <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy On Koyeb">
</a></p>
<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʀᴀɪʟᴡᴀʏ 」─
</h3>
<p align="center"><a href="https://railway.app/deploy?template="https://github.com/Codeflix-Bots/FileStore/tree/multi-fsub">
     <img height="45px" src="https://railway.app/button.svg">
</a></p>
<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʀᴇɴᴅᴇʀ 」─
</h3>
<p align="center"><a href="https://render.com/deploy?repo=https://github.com/Codeflix-Bots/FileStore/tree/multi-fsub">
<img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
</a></p>
<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ᴠᴘs 」─
</h3>
<p>
<pre>
git clone https://github.com/Codeflix-Bots/FileStore/tree/multi-fsub
# Install Packages
pip3 install -U -r requirements.txt
Edit info.py with variables as given below then run bot
python3 bot.py
</pre>
</p>
</details>

### Admin Commands

```
start - start the bot or get posts
batch - create link for more than one posts
genlink - create link for one post
users - view bot statistics
broadcast - broadcast any messages to bot users
stats - checking your bot uptime
```

### Variables

* `API_HASH` Your API Hash from my.telegram.org
* `APP_ID` Your API ID from my.telegram.org
* `TG_BOT_TOKEN` Your bot token from @BotFather
* `OWNER_ID` Must enter Your Telegram Id
* `CHANNEL_ID` Your Channel ID eg:- -100xxxxxxxx
* `DATABASE_URL` Your mongo db url
* `DATABASE_NAME` Your mongo db session name
* `ADMINS` Optional: A space separated list of user_ids of Admins, they can only create links
* `START_MESSAGE` Optional: start message of bot, use HTML and <a href='https://github.com/codexbotz/File-Sharing-Bot/blob/main/README.md#start_message'>fillings</a>
* `FORCE_SUB_MESSAGE`Optional:Force sub message of bot, use HTML and Fillings
* `FORCE_SUB_CHANNEL_1` Required: 1st ForceSub Channel ID
* `FORCE_SUB_CHANNEL_2` Required: 2nd ForceSub Channel ID
* `FORCE_SUB_CHANNEL_3` Required: 3rd ForceSub Channel ID
* `FORCE_SUB_CHANNEL_4` Required: 4th ForceSub Channel ID
* `PROTECT_CONTENT` Optional: True if you need to prevent files from forwarding

### Extra Variables

* `CUSTOM_CAPTION` put your Custom caption text if you want Setup Custom Caption, you can use HTML and <a href='https://github.com/CodeXBotz/File-Sharing-Bot/blob/main/README.md#custom_caption'>fillings</a> for formatting (only for documents)
* `DISABLE_CHANNEL_BUTTON` Put True to Disable Channel Share Button, Default if False
* `BOT_STATS_TEXT` put your custom text for stats command, use HTML and <a href='https://github.com/codexbotz/File-Sharing-Bot/blob/main/README.md#custom_stats'>fillings</a>
* `USER_REPLY_TEXT` put your text to show when user sends any message, use HTML


## 𝐶𝑜𝑚𝑚𝑎𝑛𝑑𝑠

```
/start - start the bot or get posts
/batch - create link for more than one posts
/genlink - create link for one post
/users - view bot statistics
/broadcast - broadcast any messages to bot users
/stats - checking your bot uptime
```

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">
#ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴍʏ ᴄʀᴇᴅɪᴛ...

</b>⋗  ᴛᴇʟᴇɢʀᴀᴍ - <b>[ᴄᴏᴅᴇғʟɪx ʙᴏᴛs](https://t.me/codeflix_bots)</b>


- ᴄʀᴇᴅɪᴛ <b>[ᴄᴏᴅᴇғʟɪx ʙᴏᴛs](https://t.me/codeflix_bots)  ➻  [ᴏᴡɴᴇʀ](https://t.me/sewxiy) </b>
- ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛ..
- ᴛʜᴀɴᴋ ʏᴏᴜ ᴄᴏᴅᴇғʟɪx ʙᴏᴛs ғᴏʀ ʜᴇʟᴘɪɴɢ ᴜs ɪɴ ᴛʜɪs ᴊᴏᴜʀɴᴇʏ 
- ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ɢɪᴠɪɴɢ ᴍᴇ ᴄʀᴇᴅɪᴛ @Codeflix-bots  
- ғᴏʀ ᴀɴʏ ᴇʀʀᴏʀ ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ -> ᴛᴇʟᴇɢʀᴀᴍ @codeflix_bots Community @Otakflix_Network </b>

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">


<h3>「 ᴄʀᴇᴅɪᴛs 」
</h3>

- <b>[ᴄᴏᴅᴇғʟɪx ʙᴏᴛs](https://t.me/codeflix_bots)  ➻  [ʙᴀsᴇ ᴄᴏᴅᴇ](https://t.me/codeflix_bots) </b>
- <b>[ᴍɪᴋᴇʏ](https://github.com/erotixe)  ➻  [ᴇᴠᴇʀʏᴛʜɪɴɢ](https://t.me/veldxd) </b>
 
<b>ᴀɴᴅ ᴀʟʟ [ᴛʜᴇ ᴄᴏɴᴛʀɪʙᴜᴛᴏʀs](https://telegram.me/codeflix-bots) ᴡʜᴏ ʜᴇʟᴩᴇᴅ ɪɴ ᴍᴀᴋɪɴɢ multi fsub ʙᴏᴛ ᴜsᴇꜰᴜʟ & ᴩᴏᴡᴇʀꜰᴜʟ 🖤 </b>

## 📌  𝑵𝒐𝒕𝒆

ᴊᴜꜱᴛ ꜰᴏʀᴋ ᴛʜᴇ ʀᴇᴘᴏ ᴀɴᴅ ᴇᴅɪᴛ ᴀꜱ ᴘᴇʀ ʏᴏᴜʀ ɴᴇᴇᴅꜱ.

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">
