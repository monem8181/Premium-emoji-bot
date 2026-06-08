import logging
import random
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS_RAW = os.environ.get("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",")]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PREMIUM EMOJI — ID + actual emoji mapped
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# { emoji_id: fallback_char }  ← screenshot থেকে দেখা actual emoji
PREMIUM_EMOJIS = {
    5956451368410549960: "✨",   # sparkle/dot
    5260416304224936047: "✅",   # circle check
    5956127068314930874: "✅",   # green check
    5267031043487051884: "💘",   # heart ribbon
    5447153029759397673: "👍",   # thumbs up
    5447128406711891434: "👎",   # thumbs down
    5958741397728137162: "🎉",   # party popper
    6224522392140518274: "🥳",   # party face
    6280737226213036548: "🤩",   # star struck
    6107379594388572414: "🇺🇸",  # flag (US style)
    6246800353145131896: "⬆️",   # blue up arrow
    6321011177497302833: "➡️",   # orange arrow
    5400332547588627951: "🐥",   # chick
    5305405309261461210: "🤔",   # thinking chick
    5219860474237044895: "🤫",   # shushing
    6334468336532850847: "😶",   # face mask
    5305388752162539722: "😷",   # mask face
    6023924329673135034: "💗",   # pink heart
    6026236216079290036: "💜",   # purple heart
    5413694143601842851: "🔥",   # fire/flame
    6100570924468145091: "🐸",   # pepe/frog
    5210952531676504517: "❌",   # red X
}

def pe(emoji_id: int) -> str:
    """Premium emoji tag বানায়।"""
    fallback = PREMIUM_EMOJIS.get(emoji_id, "⭐")
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

# Shortcut variables — নাম দিয়ে সহজে ব্যবহার করা যাবে
E_SPARKLE  = pe(5956451368410549960)
E_CHECK    = pe(5260416304224936047)
E_GCHECK   = pe(5956127068314930874)
E_HEART    = pe(5267031043487051884)
E_THUMBSUP = pe(5447153029759397673)
E_PARTY    = pe(5958741397728137162)
E_PARTY2   = pe(6224522392140518274)
E_STARSTRUCK = pe(6280737226213036548)
E_ARROW_UP = pe(6246800353145131896)
E_ARROW    = pe(6321011177497302833)
E_CHICK    = pe(5400332547588627951)
E_THINK    = pe(5305405309261461210)
E_SHUSH    = pe(5219860474237044895)
E_PINKHEART = pe(6023924329673135034)
E_PURPLEHEART = pe(6026236216079290036)
E_FIRE     = pe(5413694143601842851)
E_PEPE     = pe(6100570924468145091)
E_CROSS    = pe(5210952531676504517)

ALL_IDS = list(PREMIUM_EMOJIS.keys())

def rand_emoji() -> str:
    return pe(random.choice(ALL_IDS))

def rand_emojis(count: int = 3) -> str:
    return " ".join(pe(e) for e in random.sample(ALL_IDS, min(count, len(ALL_IDS))))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONTENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JOKES = [
    "প্রোগ্রামার কেন বাথরুমে যায় না?\nকারণ সে বলে — 'এখনো loop শেষ হয়নি!' 😂",
    "Teacher: তুমি কি জানো পৃথিবী কত বড়?\nStudent: আমার internet connection যত slow, পৃথিবী তত বড় মনে হয়!",
    "আমি diet শুরু করেছি।\nপ্রথম দিন: শুধু সালাদ।\nদ্বিতীয় দিন: সালাদ আর একটু ভাত।\nতৃতীয় দিন: diet শেষ।",
    "বন্ধু: তুই রোজ late কেন?\nআমি: সময়মতো আসি, কিন্তু সময়টাই এগিয়ে যায়!",
    "Math exam এ গেছি।\nQuestion: x খুঁজে বের করো।\nআমি: 'এইখানে আছে' বলে arrow দিলাম। ✓",
    "WhatsApp এ 'typing...' দেখা যাচ্ছে ১০ মিনিট ধরে।\nশেষে message আসলো: 'k'",
    "আমার phone এ ৯৭% storage full।\n৩% দিয়ে কী করবো?\nRemind me later তে click করবো।",
]

QUOTES = [
    "সাফল্য মানে পড়ে না যাওয়া নয়, বরং প্রতিবার উঠে দাঁড়ানো। — Nelson Mandela",
    "স্বপ্ন দেখো, কারণ স্বপ্নই তোমাকে এগিয়ে নিয়ে যাবে। — A.P.J. Abdul Kalam",
    "কঠিন সময়ে হাল ছেড়ো না, ঝড়ের পরেই রোদ ওঠে।",
    "তুমি যা ভাবো, তুমি তাই হয়ে ওঠো। — Buddha",
    "প্রতিটি বিশেষজ্ঞই একসময় নতুন শিক্ষার্থী ছিল।",
    "সময় নষ্ট করা মানে জীবন নষ্ট করা।",
    "ভুল করা মানে হেরে যাওয়া নয়, না চেষ্টা করাটাই হার।",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  USER TRACKING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
user_db: dict = {}

def track_user(user):
    uid = user.id
    if uid not in user_db:
        user_db[uid] = {
            "name": user.first_name or "Unknown",
            "username": user.username or "N/A",
            "count": 0,
        }
    user_db[uid]["count"] += 1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main_keyboard():
    keyboard = [
        [KeyboardButton("😂 Joke"), KeyboardButton("💬 Quote")],
        [KeyboardButton("🎲 Random Emoji"), KeyboardButton("ℹ️ Help")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COMMAND HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    track_user(user)
    name = user.first_name or "বন্ধু"
    text = (
        f"{E_PARTY} {E_STARSTRUCK} {E_PARTY2}\n\n"
        f"<b>স্বাগতম, {name}!</b>\n\n"
        f"আমি তোমার personal assistant bot {E_CHECK}\n\n"
        f"{E_FIRE} <b>আমি যা করতে পারি:</b>\n"
        f"  {E_GCHECK} /joke — মজার জোকস\n"
        f"  {E_GCHECK} /quote — অনুপ্রেরণার উক্তি\n"
        f"  {E_GCHECK} /emoji — সব premium emoji\n"
        f"  {E_GCHECK} /help — সব commands\n\n"
        f"{E_ARROW} {E_ARROW} নিচের বাটন ব্যবহার করো!"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard())

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    selected = random.choice(JOKES)
    text = (
        f"{E_PARTY} <b>জোকস টাইম!</b>\n\n"
        f"{selected}\n\n"
        f"{E_THUMBSUP} {E_STARSTRUCK}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    selected = random.choice(QUOTES)
    text = (
        f"{E_SPARKLE} <b>আজকের উক্তি</b>\n\n"
        f"<i>❝ {selected} ❞</i>\n\n"
        f"{E_PINKHEART} {E_PURPLEHEART}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def show_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    all_emojis = " ".join(pe(eid) for eid in ALL_IDS)
    text = (
        f"{E_FIRE} <b>সব Premium Animated Emojis:</b>\n\n"
        f"{all_emojis}\n\n"
        f"মোট: <b>{len(ALL_IDS)}টি</b> premium emoji {E_CHECK}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    text = (
        f"{E_PARTY} {E_STARSTRUCK} {E_FIRE}\n\n"
        f"<b>📋 সব Commands:</b>\n\n"
        f"{E_GCHECK} /start — বট শুরু করো\n"
        f"{E_GCHECK} /joke — মজার জোকস পাও\n"
        f"{E_GCHECK} /quote — অনুপ্রেরণার কথা\n"
        f"{E_GCHECK} /emoji — সব premium emoji দেখো\n"
        f"{E_GCHECK} /help — এই মেনু\n\n"
        f"👑 <b>Admin Commands:</b>\n"
        f"{E_ARROW} /broadcast [msg] — সবাইকে message\n"
        f"{E_ARROW} /stats — bot statistics\n"
        f"{E_ARROW} /users — সব users এর list\n\n"
        f"{E_PINKHEART} {E_PURPLEHEART}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard())

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E_CROSS} তুমি admin নও!")
        return
    text = (
        f"{E_FIRE} {E_STARSTRUCK}\n\n"
        f"<b>📊 Bot Statistics</b>\n\n"
        f"{E_GCHECK} Total Users: <b>{len(user_db)}</b>\n"
        f"{E_GCHECK} Premium Emojis: <b>{len(ALL_IDS)}টি</b>\n"
        f"{E_GCHECK} Jokes: <b>{len(JOKES)}টি</b>\n"
        f"{E_GCHECK} Quotes: <b>{len(QUOTES)}টি</b>\n\n"
        f"Bot চলছে Railway-তে {E_CHECK}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E_CROSS} তুমি admin নও!")
        return
    if not user_db:
        await update.message.reply_text(f"{E_THINK} এখনো কোনো user নেই!")
        return
    lines = [f"{E_FIRE} <b>User List ({len(user_db)} জন):</b>\n"]
    for uid, info in list(user_db.items())[:20]:
        lines.append(f"{E_ARROW} <b>{info['name']}</b> (@{info['username']}) — {info['count']} msg")
    if len(user_db) > 20:
        lines.append(f"\n...আরো {len(user_db) - 20} জন আছে।")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E_CROSS} তুমি admin নও!")
        return
    if not context.args:
        await update.message.reply_text(
            f"{E_THINK} Usage: /broadcast [message]\n\nExample:\n/broadcast হ্যালো সবাই!"
        )
        return
    msg = " ".join(context.args)
    broadcast_text = (
        f"{E_PARTY} {E_STARSTRUCK}\n\n"
        f"<b>📢 Broadcast</b>\n\n"
        f"{msg}\n\n"
        f"{E_PINKHEART} {E_PURPLEHEART}"
    )
    sent = 0
    failed = 0
    for uid in user_db:
        try:
            await context.bot.send_message(chat_id=uid, text=broadcast_text, parse_mode=ParseMode.HTML)
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(
        f"{E_GCHECK} Broadcast শেষ!\n{E_CHECK} Sent: <b>{sent}</b>\n{E_CROSS} Failed: <b>{failed}</b>",
        parse_mode=ParseMode.HTML
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    text = update.message.text
    if text == "😂 Joke":
        await joke(update, context)
    elif text == "💬 Quote":
        await quote(update, context)
    elif text == "🎲 Random Emoji":
        emojis = rand_emojis(6)
        await update.message.reply_text(
            f"{E_FIRE} <b>Random Premium Emojis:</b>\n\n{emojis}",
            parse_mode=ParseMode.HTML
        )
    elif text == "ℹ️ Help":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            f"{E_THINK} বুঝলাম না! /help দিয়ে দেখো কী কী করা যায়।",
            parse_mode=ParseMode.HTML
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ BOT_TOKEN set koro! Railway Variables-e BOT_TOKEN add koro.")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("emoji", show_emoji))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("users", users_list))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    print("🤖 Bot চালু! Railway-তে running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
