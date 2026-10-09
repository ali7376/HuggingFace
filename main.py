"""Terminal version of the assistant:  python main.py [--provider groq]"""

import argparse

from chatbot import Chatbot
from config import APP_NAME, PROVIDERS, available_providers
from providers import ProviderError


def main() -> None:
    parser = argparse.ArgumentParser(description=f"{APP_NAME} (terminal)")
    parser.add_argument(
        "--provider",
        choices=list(PROVIDERS),
        help="AI provider to use (default: first one with an API key)",
    )
    args = parser.parse_args()

    if not available_providers():
        print("No API key found. Copy .env.example to .env and add a key.")
        return

    try:
        bot = Chatbot(args.provider)
    except ProviderError as error:
        print(error)
        return

    print(f"{APP_NAME}  |  {bot.provider.label}  |  {bot.provider.model}")
    print("Commands: reset, exit")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command in {"exit", "quit"}:
            print("Goodbye!")
            break

        if command == "reset":
            bot.reset()
            print("Conversation memory cleared.")
            continue

        try:
            print(f"\n{APP_NAME}: {bot.reply(user_input)}")
        except Exception as error:
            print(f"\nRequest failed: {error}")


if __name__ == "__main__":
    main()
