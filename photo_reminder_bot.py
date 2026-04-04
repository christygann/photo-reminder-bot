import logging
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
import os

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = int(os.environ["GROUP_CHAT_ID"])        # Your group chat ID (negative number)
REMINDER_MESSAGE = "📸 Time to send a photo!"
REMINDER_INTERVAL_SECONDS = 4*3600       # 1 hour = 3600 seconds
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the hourly photo reminder to the group."""
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=REMINDER_MESSAGE
    )
    logger.info("Reminder sent to group chat.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command — confirms the bot is running."""
    await update.message.reply_text(
        "✅ Photo reminder bot is running! I'll remind the group every hour to send a photo."
    )


async def stop_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stop command — removes the hourly job."""
    jobs = context.job_queue.get_jobs_by_name("hourly_reminder")
    if jobs:
        for job in jobs:
            job.schedule_removal()
        await update.message.reply_text("⏹ Hourly reminders stopped.")
    else:
        await update.message.reply_text("No active reminders found.")


async def start_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /startreminders command — starts or restarts the hourly job."""
    # Remove any existing jobs first to avoid duplicates
    for job in context.job_queue.get_jobs_by_name("hourly_reminder"):
        job.schedule_removal()

    context.job_queue.run_repeating(
        send_reminder,
        interval=REMINDER_INTERVAL_SECONDS,
        first=10,  # Send first reminder 10 seconds after command
        name="hourly_reminder"
    )
    await update.message.reply_text("▶️ Hourly photo reminders started!")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("startreminders", start_reminders))
    app.add_handler(CommandHandler("stop", stop_reminders))

    # Schedule the hourly reminder to start automatically on bot launch
    job_queue = app.job_queue
    job_queue.run_repeating(
        send_reminder,
        interval=REMINDER_INTERVAL_SECONDS,
        first=10,  # First reminder 10 seconds after bot starts
        name="hourly_reminder"
    )

    logger.info("Bot started. Sending reminders every hour.")
    app.run_polling()


if __name__ == "__main__":
    main()
