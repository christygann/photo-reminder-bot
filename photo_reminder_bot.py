import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

load_dotenv()

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = int(os.environ["GROUP_CHAT_ID"])
REMINDER_MESSAGE = "IT'S PHOTO TIME EVERYBODYYYYYY 📸📸📸📸📸📸"
INTERVAL_HOURS = 4
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

reminder_running = False
reminder_task = None


async def reminder_loop(bot) -> None:
    await asyncio.sleep(10)
    while reminder_running:
        try:
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=REMINDER_MESSAGE)
            logger.info(f"Reminder sent. Next in {INTERVAL_HOURS} hour(s).")
        except Exception as e:
            logger.error(f"Failed to send reminder: {e}")
        await asyncio.sleep(INTERVAL_HOURS * 3600)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome! Here are the available commands:\n\n"
        "/startreminders - Start reminders\n"
        "/stop - Stop reminders\n"
        "/status - Check current reminder status"
    )


async def start_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global reminder_running, reminder_task

    if reminder_running:
        await update.message.reply_text("⚠️ Reminders are already running!")
        return

    reminder_running = True
    reminder_task = asyncio.create_task(reminder_loop(context.bot))
    await update.message.reply_text(f"▶️ Reminders started! Sending every {INTERVAL_HOURS} hours.")


async def stop_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global reminder_running, reminder_task

    if not reminder_running:
        await update.message.reply_text("⚠️ No reminders are currently running.")
        return

    reminder_running = False
    if reminder_task:
        reminder_task.cancel()
    await update.message.reply_text("⏹ Reminders stopped.")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = "▶️ Running" if reminder_running else "⏹ Stopped"
    await update.message.reply_text(
        f"Status: {state}\n"
        f"Interval: every {INTERVAL_HOURS} hours"
    )


async def main() -> None:
    global reminder_running, reminder_task

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("startreminders", start_reminders))
    app.add_handler(CommandHandler("stop", stop_reminders))
    app.add_handler(CommandHandler("status", status))

    async with app:
        await app.start()
        reminder_running = True
        reminder_task = asyncio.create_task(reminder_loop(app.bot))
        logger.info(f"Bot started. Sending reminders every {INTERVAL_HOURS} hours.")
        await app.updater.start_polling()
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())