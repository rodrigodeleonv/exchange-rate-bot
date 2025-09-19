"""Exchange Rate Bot Scheduler Application.

This application runs a scheduler that sends daily exchange rate notifications using APScheduler.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from apps.daily_notifier_app import DailyNotifierApp
from src.config import get_config

# TODO: centralize logging configuration
logging.basicConfig(
    level=get_config().log.level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scheduler.log"),
    ],
)
logger = logging.getLogger(__name__)


class ExchangeRateScheduler:
    """Scheduler for daily exchange rate notifications."""

    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.notifier_app = DailyNotifierApp()
        self.timezone = ZoneInfo(get_config().server.timezone)
        self._shutdown_requested = False

        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: object) -> None:
        """Handle shutdown signals gracefully."""
        logger.info("🛑 Received shutdown signal (%s), stopping scheduler...", signum)
        self._shutdown_requested = True

    def _setup_jobs(self) -> None:
        """Setup scheduled jobs."""
        self.scheduler.add_job(
            func=self.daily_notification_job,
            trigger=CronTrigger(hour=8, minute=0, second=0, timezone=self.timezone),
            id="daily_rates_notification",
            name="Daily Exchange Rates Notification",
            replace_existing=True,
            max_instances=1,  # Prevent overlapping executions
            misfire_grace_time=300,  # 5 minutes grace time for missed jobs
        )

        logger.info("✅ Scheduled daily notifications for 8:00 AM Guatemala time")

    async def daily_notification_job(self) -> None:
        """Job function that runs daily at 8:00 AM."""
        try:
            current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S %Z")
            logger.info("⏰ Executing daily notification job at %s", current_time)

            sent_count, error_count = await self.notifier_app.send_daily_rates_notification()

            logger.info("📊 Daily job completed - Sent: %s, Errors: %s", sent_count, error_count)

        except Exception as e:
            logger.error("❌ Error in daily notification job: %s", e, exc_info=True)

    async def start(self) -> None:
        """Start the scheduler."""
        try:
            logger.info("🚀 Starting Exchange Rate Scheduler...")

            # Setup jobs
            self._setup_jobs()

            # Start scheduler
            self.scheduler.start()

            # Log next run time
            job = self.scheduler.get_job("daily_rates_notification")
            if job and hasattr(job, "next_run_time") and job.next_run_time:
                next_run_str = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S %Z")
                logger.info("📅 Next daily notification scheduled for: %s", next_run_str)

            logger.info("✅ Scheduler started successfully")
            logger.info("🔄 Scheduler is running... Press Ctrl+C to stop")

            # Keep the scheduler running
            while not self._shutdown_requested:
                await asyncio.sleep(1)  # Check every second for shutdown

            await self.shutdown()

        except Exception as e:
            logger.error("❌ Error starting scheduler: %s", e, exc_info=True)
            await self.shutdown()

    async def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        try:
            logger.info("🛑 Shutting down scheduler...")

            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("✅ Scheduler stopped")

            # Close notifier app
            await self.notifier_app.close()
            logger.info("✅ Notifier app closed")

            logger.info("👋 Scheduler shutdown complete")

        except Exception as e:
            logger.error("❌ Error during shutdown: %s", e, exc_info=True)
        finally:
            # Force exit if needed
            sys.exit(0)

    async def run_once(self) -> None:
        """Run the daily notification job once (for testing)."""
        logger.info("🧪 Running daily notification job once for testing...")
        await self.daily_notification_job()
        await self.notifier_app.close()


async def main() -> None:
    """Main entry point for the scheduler application."""
    scheduler_app = ExchangeRateScheduler()

    # Check if we want to run once for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--run-once":
        await scheduler_app.run_once()
        return

    # Start the scheduler
    await scheduler_app.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Scheduler stopped by user")
    except Exception as e:
        logger.error("❌ Fatal error: %s", e, exc_info=True)
        sys.exit(1)
