"""Main entry points for different applications."""

import sys

from apps.daily_notifier_app import main_daily, main_startup
from apps.webhook_app import main as webhook_main


def print_help():
    """Print usage help."""
    print("🤖 Exchange Rate Bot - Application Launcher")
    print("")
    print("Usage: python main.py [command]")
    print("")
    print("Commands:")
    print("  webhook  🌐 Start FastAPI webhook server (default)")
    print("  daily    📊 Send daily exchange rates notification")
    print("  startup  🚀 Send startup notification (legacy)")
    print("  help     ❓ Show this help message")
    print("")
    print("Examples:")
    print("  python main.py           # Start webhook server")
    print("  python main.py webhook   # Start webhook server")
    print("  python main.py daily     # Send daily notification")
    print("")


def main():
    """Main entry point with command selection."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "webhook":
            print("🌐 Starting webhook server...")
            webhook_main()
        elif command == "daily":
            print("📊 Sending daily rates notification...")
            main_daily()
        elif command == "startup":
            print("🚀 Sending startup notification...")
            main_startup()
        elif command in ["help", "-h", "--help"]:
            print_help()
        else:
            print(f"❌ Unknown command: {command}")
            print("")
            print_help()
            sys.exit(1)
    else:
        # Default to webhook
        print("🌐 Starting webhook server (default)...")
        webhook_main()


if __name__ == "__main__":
    main()
