import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.environ["BOT_TOKEN"]

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أرسل رابط فيديو TikTok وسأحاول تنزيله لك 🎬"
    )

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "tiktok.com" not in url:
        await update.message.reply_text("أرسل رابط TikTok صحيحًا.")
        return

    msg = await update.message.reply_text("⏳ جارٍ تنزيل الفيديو...")

    filename = f"/tmp/{update.effective_user.id}.mp4"

    try:
        options = {
            "format": "mp4[filesize<45M]/best[filesize<45M]",
            "outtmpl": filename,
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        await msg.edit_text("✅ تم التنزيل، جارٍ الإرسال...")

        with open(filename, "rb") as video:
            await update.message.reply_video(video=video)

        os.remove(filename)

    except Exception:
        await msg.edit_text(
            "❌ لم أستطع تنزيل هذا الفيديو. جرّب رابط TikTok آخر."
        )

def main():
    threading.Thread(target=run_web, daemon=True).start()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok)
    )

    application.run_polling()

if __name__ == "__main__":
    main()
