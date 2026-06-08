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
#  CONFIG — Railway environment variables
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS_RAW = os.environ.get("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",")]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PREMIUM ANIMATED EMOJI IDs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREMIUM_EMOJIS = [
    5956451368410549960,
    5260416304224936047,
    5956127068314930874,
    5267031043487051884,
    5447153029759397673,
    5447128406711891434,
    5958741397728137162,
    6224522392140518274,
    6280737226213036548,
    6107379594388572414,
    6246800353145131896,
    6321011177497302833,
    5400332547588627951,
    5305405309261461210,
    5219860474237044895,
    6334468336532850847,
    5305388752162539722,
    6023924329673135034,
    6026236216079290036,
    5413694143601842851,
    6100570924468145091,
    5210952531676504517,
]

def premium_emoji(emoji_id: int) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">⭐</tg-emoji>'

def rand_emoji() -> str:
    return premium_emoji(random.choice(PREMIUM_EMOJIS))

def rand_emojis(count: int = 3) -> str:
    return " ".join(premium_emoji(e) for e in random.sample(PREMIUM_EMOJIS, min(count, len(PREMIUM_EMOJIS))))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  JOKES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JOKES = [
    "প্রোগ্রামার কেন বাথরুমে যায় না?\nকারণ সে বলে — 'এখনো loop শেষ হয়নি!' 😂",
    "Teacher: তুমি কি জানো পৃথিবী কত বড়?\nStudent: হ্যাঁ! আমার internet connection যত slow, পৃথিবী তত বড় মনে হয়!",
    "আমি diet শুরু করেছি।\nপ্রথম দিন: শুধু সালাদ।\nদ্বিতীয় দিন: সালাদ আর একটু ভাত।\nতৃতীয় দিন: diet শেষ।",
    "বন্ধু: তুই রোজ late কেন?\nআমি: সময়মতো আসি, কিন্তু সময়টাই এগিয়ে যায়!",
    "Math exam দিতে গেছি।\nQuestion: x খুঁজে বের করো।\nআমি: 'এইখানে আছে' বলে arrow দিলাম। ✓",
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
#  USER TRACKING (in-memory)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
user_db: dict = {}  # { user_id: {"name": ..., "username": ..., "count": ...} }

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
#  HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    track_user(user)
    name = user.first_name or "বন্ধু"
    text = (
        f"{rand_emojis(3)}\n\n"
        f"<b>স্বাগতম, {name}!</b>\n\n"
        f"আমি তোমার personal assistant bot {rand_emoji()}\n\n"
        f"{rand_emoji()} <b>আমি যা করতে পারি:</b>\n"
        f"  /joke — মজার জোকস\n"
        f"  /quote — অনুপ্রেরণার উক্তি\n"
        f"  /emoji — সব premium emoji\n"
        f"  /help — সব commands\n\n"
        f"{rand_emojis(2)} নিচের বাটন ব্যবহার করো!"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard())

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    selected = random.choice(JOKES)
    text = f"{rand_emoji()} <b>জোকস টাইম!</b>\n\n{selected}\n\n{rand_emojis(2)}"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    selected = random.choice(QUOTES)
    text = f"{rand_emoji()} <b>আজকের উক্তি</b>\n\n<i>❝ {selected} ❞</i>\n\n{rand_emojis(2)}"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def show_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    all_emojis = " ".join(premium_emoji(e) for e in PREMIUM_EMOJIS)
    text = (
        f"<b>✨ সব Premium Animated Emojis:</b>\n\n"
        f"{all_emojis}\n\n"
        f"মোট: <b>{len(PREMIUM_EMOJIS)}টি</b> premium emoji!"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user)
    text = (
        f"{rand_emojis(3)}\n\n"
        f"<b>📋 সব Commands:</b>\n\n"
        f"{rand_emoji()} /start — বট শুরু করো\n"
        f"{rand_emoji()} /joke — মজার জোকস পাও\n"
        f"{rand_emoji()} /quote — অনুপ্রেরণার কথা\n"
        f"{rand_emoji()} /emoji — সব premium emoji দেখো\n"
        f"{rand_emoji()} /help — এই মেনু\n\n"
        f"<b>👑 Admin Commands:</b>\n"
        f"{rand_emoji()} /broadcast [message] — সবাইকে message পাঠাও\n"
        f"{rand_emoji()} /stats — bot statistics\n"
        f"{rand_emoji()} /users — সব users এর list\n\n"
        f"{rand_emojis(2)}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard())

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{rand_emoji()} তুমি admin নও!")
        return
    text = (
        f"{rand_emojis(2)}\n\n"
        f"<b>📊 Bot Statistics</b>\n\n"
        f"{rand_emoji()} Total Users: <b>{len(user_db)}</b>\n"
        f"{rand_emoji()} Premium Emojis: <b>{len(PREMIUM_EMOJIS)}টি</b>\n"
        f"{rand_emoji()} Jokes: <b>{len(JOKES)}টি</b>\n"
        f"{rand_emoji()} Quotes: <b>{len(QUOTES)}টি</b>\n\n"
        f"Bot চলছে Railway-তে {rand_emoji()}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{rand_emoji()} তুমি admin নও!")
        return
    if not user_db:
        await update.message.reply_text(f"{rand_emoji()} এখনো কোনো user নেই!")
        return
    lines = [f"{rand_emoji()} <b>User List ({len(user_db)} জন):</b>\n"]
    for uid, info in list(user_db.items())[:20]:  # max 20 show
        lines.append(f"• <b>{info['name']}</b> (@{info['username']}) — {info['count']} messages")
    if len(user_db) > 20:
        lines.append(f"\n...আরো {len(user_db) - 20} জন আছে।")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{rand_emoji()} তুমি admin নও!")
        return
    if not context.args:
        await update.message.reply_text(
            f"{rand_emoji()} Usage: /broadcast [তোমার message]\n\nExample:\n/broadcast হ্যালো সবাই!"
        )
        return
    msg = " ".join(context.args)
    broadcast_text = (
        f"{rand_emojis(2)}\n\n"
        f"<b>📢 Broadcast</b>\n\n"
        f"{msg}\n\n"
        f"{rand_emoji()}"
    )
    sent = 0
    failed = 0
    for uid in user_db:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=broadcast_text,
                parse_mode=ParseMode.HTML
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"{rand_emoji()} Broadcast শেষ!\n✅ Sent: <b>{sent}</b>\n❌ Failed: <b>{failed}</b>",
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
        emojis = rand_emojis(5)
        await update.message.reply_text(
            f"<b>🎲 Random Premium Emojis:</b>\n\n{emojis}",
            parse_mode=ParseMode.HTML
        )
    elif text == "ℹ️ Help":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            f"{rand_emoji()} বুঝলাম না! /help দিয়ে দেখো কী কী করা যায়।",
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
