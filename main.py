"""Main entry points for different applications."""

import sys

from apps.webhook_app import main as webhook_main


def print_help():
    """Print usage help."""
    print("🤖 Exchange Rate Bot - Application Launcher")
    print("")
    print("Usage: python main.py [command]")
    print("")
    print("Commands:")
    print("  webhook  🌐 Start FastAPI webhook server (default)")
    print("  help     ❓ Show this help message")
    print("")
    print("Examples:")
    print("  python main.py           # Start webhook server")
    print("  python main.py webhook   # Start webhook server")
    print("")
    print("For scheduling daily notifications, use:")
    print("  python -m apps.scheduler_app")
    print("")


def main():
    """Main entry point with command selection."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "webhook":
            print("🌐 Starting webhook server...")
            webhook_main()
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
