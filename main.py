import os
import re
import asyncio
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي أي رابط فيديو (تيك توك، يوتيوب، إنستغرام...) وسأقوم بتحميله لك مباشرة.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not re.match(r'https?://[^\s]+', url):
        return
    
    msg = await update.message.reply_text("جاري تحميل الفيديو، انتظر لحظة...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'max_filesize': 50 * 1024 * 1024,
        }
        try:
            loop = asyncio.get_running_loop()
            def run_dl():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info)
            
            filepath = await loop.run_in_executor(None, run_dl)
            await msg.edit_text("جاري رفع الفيديو إلى تليجرام...")
            with open(filepath, 'rb') as video_file:
                await update.message.reply_video(video=video_file)
            await msg.delete()
        except Exception as e:
            await msg.edit_text("عذراً، حدث خطأ أثناء التحميل أو الملف أكبر من الحد المسموح.")

def main():
    if not TOKEN:
        print("خطأ: لم يتم العثور على TELEGRAM_BOT_TOKEN في المتغيرات البيئية!")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()

if __name__ == "__main__":
    main()
