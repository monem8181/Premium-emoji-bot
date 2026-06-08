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
#  PREMIUM EMOJI MAP — ID + actual emoji
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREMIUM_EMOJIS = {
    # === BATCH 1 (original 22) ===
    5956451368410549960: "✨",
    5260416304224936047: "✅",
    5956127068314930874: "✅",
    5267031043487051884: "💘",
    5447153029759397673: "👍",
    5447128406711891434: "👎",
    5958741397728137162: "🎉",
    6224522392140518274: "🥳",
    6280737226213036548: "🤩",
    6107379594388572414: "🇺🇸",
    6246800353145131896: "⬆️",
    6321011177497302833: "➡️",
    5400332547588627951: "🐥",
    5305405309261461210: "🤔",
    5219860474237044895: "🤫",
    6334468336532850847: "😶",
    5305388752162539722: "😷",
    6023924329673135034: "💗",
    6026236216079290036: "💜",
    5413694143601842851: "🔥",
    6100570924468145091: "🐸",
    5210952531676504517: "❌",
    # === BATCH 2 (নতুন ৬টি) ===
    5416132628464020245: "🤣",   # rolling on floor laughing
    5325799368761027493: "😆",   # laughing face red
    5366268406049820413: "ℹ️",   # info blue circle
    5452026937172048380: "ℹ️",   # info blue circle 2
    5260535596941582167: "💬",   # speech bubble
    5805400409447075159: "⚡",   # lightning bolt
}

def pe(emoji_id: int) -> str:
    fallback = PREMIUM_EMOJIS.get(emoji_id, "⭐")
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

ALL_IDS = list(PREMIUM_EMOJIS.keys())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NAMED SHORTCUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
E_SPARKLE     = pe(5956451368410549960)
E_CHECK       = pe(5260416304224936047)
E_GCHECK      = pe(5956127068314930874)
E_HEART       = pe(5267031043487051884)
E_THUMBSUP    = pe(5447153029759397673)
E_THUMBSDOWN  = pe(5447128406711891434)
E_PARTY       = pe(5958741397728137162)
E_PARTY2      = pe(6224522392140518274)
E_STARSTRUCK  = pe(6280737226213036548)
E_ARROW_UP    = pe(6246800353145131896)
E_ARROW       = pe(6321011177497302833)
E_CHICK       = pe(5400332547588627951)
E_THINK       = pe(5305405309261461210)
E_SHUSH       = pe(5219860474237044895)
E_PINKHEART   = pe(6023924329673135034)
E_PURPLEHEART = pe(6026236216079290036)
E_FIRE        = pe(5413694143601842851)
E_PEPE        = pe(6100570924468145091)
E_CROSS       = pe(5210952531676504517)
# নতুন
E_LMAO        = pe(5416132628464020245)   # 🤣
E_LAUGH       = pe(5325799368761027493)   # 😆
E_INFO        = pe(5366268406049820413)   # ℹ️
E_INFO2       = pe(5452026937172048380)   # ℹ️
E_BUBBLE      = pe(5260535596941582167)   # 💬
E_LIGHTNING   = pe(5805400409447075159)   # ⚡

def rand_emoji() -> str:
    return pe(random.choice(ALL_IDS))

def rand_emojis(count: int = 3) -> str:
    return " ".join(pe(e) for e in random.sample(ALL_IDS, min(count, len(ALL_IDS))))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONTENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JOKES = [
    (
        f"প্রোগ্রামার কেন বাথরুমে যায় না? {E_THINK}\n"
        f"কারণ — 'এখনো loop শেষ হয়নি!' {E_LMAO}"
    ),
    (
        f"Teacher: পৃথিবী কত বড়? {E_INFO}\n"
        f"Student: আমার internet যত slow, পৃথিবী তত বড়! {E_LAUGH}"
    ),
    (
        f"Diet plan: {E_FIRE}\n"
        f"দিন ১: শুধু সালাদ\n"
        f"দিন ২: সালাদ + একটু ভাত\n"
        f"দিন ৩: diet শেষ {E_LMAO}"
    ),
    (
        f"বন্ধু: তুই রোজ late কেন? {E_THINK}\n"
        f"আমি: সময়মতো আসি, সময়টাই এগিয়ে যায়! {E_LAUGH}"
    ),
    (
        f"Math exam: x খুঁজে বের করো {E_INFO}\n"
        f"আমি: 'এইখানে আছে' → arrow দিলাম {E_LMAO}"
    ),
    (
        f"WhatsApp-এ 'typing...' ১০ মিনিট ধরে {E_BUBBLE}\n"
        f"Message আসলো: 'k' {E_LAUGH}"
    ),
    (
        f"Phone-এ ৯৭% storage full {E_LIGHTNING}\n"
        f"বাকি ৩%? Remind me later! {E_LMAO}"
    ),
    (
        f"রাত ৩টায় code করছি {E_FIRE}\n"
        f"Error: missing semicolon\n"
        f"আমি ৩ ঘন্টা ধরে খুঁজছিলাম {E_LAUGH} {E_CROSS}"
    ),
]

QUOTES = [
    "সাফল্য মানে পড়ে না যাওয়া নয়, বরং প্রতিবার উঠে দাঁড়ানো। — Nelson Mandela",
    "স্বপ্ন দেখো, কারণ স্বপ্নই তোমাকে এগিয়ে নিয়ে যাবে। — A.P.J. Abdul Kalam",
    "কঠিন সময়ে হাল ছেড়ো না, ঝড়ের পরেই রোদ ওঠে।",
    "তুমি যা ভাবো, তুমি তাই হয়ে ওঠো। — Buddha",
    "প্রতিটি বিশেষজ্ঞই একসময় নতুন শিক্ষার্থী ছিল।",
    "সময় নষ্ট করা মানে জীবন নষ্ট করা।",
    "ভুল করা মানে হেরে যাওয়া নয়, না চেষ্টা করাটাই হার।",
    "বড় স্বপ্ন দেখো, ছোট শুরু করো, এখনই শুরু করো।",
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
#  KEYBOARD — premium emoji in buttons
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main_keyboard():
    keyboard = [
        [KeyboardButton(f"😂 Joke"), KeyboardButton(f"💬 Quote")],
        [KeyboardButton(f"🎲 Random Emoji"), KeyboardButton(f"ℹ️ Help")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    track_user(user)
    name = user.first_name or "বন্ধু"
    text = (
        f"{E_PARTY} {E_STARSTRUCK} {E_LIGHTNING}\n\n"
        f"<b>স্বাগতম, {name}!</b>\n\n"
        f"আমি তোমার personal assistant bot {E_CHECK}\n\n"
        f"{E_FIRE} <b>আমি যা করতে পারি:</b>\n"
        f"  {E_GCHECK} /joke — মজার জোকস\n"
        f"  {E_GCHECK} /quote — অনুপ্রেরণার উক্তি\n"
        f"  {E_GCHECK} /emoji — সব premium emoji\n"
        f"  {E_GCHECK} /help — সব commands\n\n"
        f"{E_ARROW} {E_BUBBLE} নিচের বাটন ব্যবহার করো!"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard())

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    selected = random.choice(JOKES)
    text = (
        f"{E_LMAO} {E_LAUGH} <b>জোকস টাইম!</b>\n\n"
        f"{selected}\n\n"
        f"{E_THUMBSUP} {E_STARSTRUCK}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    selected = random.choice(QUOTES)
    text = (
        f"{E_SPARKLE} {E_LIGHTNING} <b>আজকের উক্তি</b>\n\n"
        f"<i>❝ {selected} ❞</i>\n\n"
        f"{E_PINKHEART} {E_PURPLEHEART}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def show_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    all_emojis = " ".join(pe(eid) for eid in ALL_IDS)
    text = (
        f"{E_FIRE} <b>সব Premium Animated Emojis ({len(ALL_IDS)}টি):</b>\n\n"
        f"{all_emojis}\n\n"
        f"{E_GCHECK} মোট <b>{len(ALL_IDS)}টি</b> emoji available!"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    text = (
        f"{E_PARTY} {E_STARSTRUCK} {E_LIGHTNING}\n\n"
        f"<b>📋 সব Commands:</b>\n\n"
        f"{E_GCHECK} /start — বট শুরু করো\n"
        f"{E_LMAO} /joke — মজার জোকস পাও\n"
        f"{E_SPARKLE} /quote — অনুপ্রেরণার কথা\n"
        f"{E_FIRE} /emoji — সব premium emoji দেখো\n"
        f"{E_INFO} /help — এই মেনু\n\n"
        f"👑 <b>Admin Commands:</b>\n"
        f"{E_LIGHTNING} /broadcast [msg] — সবাইকে message\n"
        f"{E_ARROW} /stats — bot statistics\n"
        f"{E_BUBBLE} /users — সব users এর list\n\n"
        f"{E_PINKHEART} {E_PURPLEHEART} {E_HEART}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard())

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E_CROSS} তুমি admin নও!")
        return
    text = (
        f"{E_LIGHTNING} {E_FIRE}\n\n"
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
        lines.append(f"\n{E_INFO} ...আরো {len(user_db) - 20} জন আছে।")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E_CROSS} তুমি admin নও!")
        return
    if not context.args:
        await update.message.reply_text(
            f"{E_THINK} Usage: /broadcast [message]\nExample: /broadcast হ্যালো সবাই!"
        )
        return
    msg = " ".join(context.args)
    broadcast_text = (
        f"{E_LIGHTNING} {E_PARTY}\n\n"
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
            f"{E_LIGHTNING} <b>Random Premium Emojis:</b>\n\n{emojis}",
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

    print(f"🤖 Bot চালু! {len(ALL_IDS)}টি premium emoji loaded. Railway-তে running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
