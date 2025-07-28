import os
import json
import uuid
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# === BOT CONFIG ===
BOT_TOKEN = os.environ.get("8136778569:AAGyozMolk6ixcYPK-ZppMUvET7LH3-YSHw")
BOT_TOKEN = "8136778569:AAGyozMolk6ixcYPK-ZppMUvET7LH3-YSHw"
OWNER_ID = "8136778569"  # Only this Telegram ID can upload videos
DATA_FILE = "videos.json"

# === Load or Initialize Video Database ===
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        video_db = json.load(f)
else:
    video_db = {}

# === Save Video Database ===
def save_db():
    with open(DATA_FILE, "w") as f:
        json.dump(video_db, f)

# === /start Command (with Deep Link Support) ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        video_key = args[0]
        if video_key in video_db:
            file_id = video_db[video_key]["file_id"]
            await update.message.reply_text("🎥 Here's your video:")
            await update.message.reply_video(video=file_id)
        else:
            await update.message.reply_text("❌ Invalid or expired link.")
    else:
        await update.message.reply_text("👋 Welcome! Send me a video to generate a unique link.")

# === Handle Incoming Videos from Owner ===
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if user_id != 8136778569:
        await update.message.reply_text("⚠️ Only the owner can upload videos.")
        return

    video = update.message.video
    if not video:
        await update.message.reply_text("❌ No video received.")
        return

    file_id = video.file_id
    title = str(uuid.uuid4())[:8]  # Short unique ID

    # Save metadata
    video_db[title] = {"file_id": file_id}
    save_db()

    # Generate deep link
    bot_username = (await context.bot.get_me()).username
    deep_link = f"https://t.me/{bot_username}?start={title}"

    await update.message.reply_text(
        f"✅ Video saved!\nHere is your unique bot link:\n\n{deep_link}\n\n📌 Shrink this using ShrinkMe.io before sharing."
    )

# === Setup Bot ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))

    print("🤖 Bot is running...")
    app.run_polling()

# === Run Bot ===
if __name__ == "__main__":
    main()
