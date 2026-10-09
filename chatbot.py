from datetime import datetime

from config import APP_NAME, default_provider
from providers import BaseProvider, ProviderError, create_provider


SYSTEM_PROMPT_TEMPLATE = """
You are {app_name}, a professional AI assistant with access to a web-search tool.
Today's date is {today}.

Use the search_web tool when:
- The user asks for current, recent, or changing information.
- The user asks about news, prices, schedules, releases, or events.
- You are uncertain whether your existing knowledge is accurate.
- The user explicitly asks you to search the web.

Do not search when:
- The user asks for creative writing.
- The question can be answered reliably without current information.
- The user asks you not to search.

When you use web search:
- Base your factual claims on the returned search results.
- Include clickable Markdown source links.
- Use the format [Source title](https://example.com).
- Never invent a URL or source.
- Explain when the search results are insufficient.
- Remember that search snippets may not contain the full webpage.

Give accurate, clear, and concise answers. Use a professional, friendly tone.
""".strip()


def build_system_prompt() -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        app_name=APP_NAME,
        today=datetime.now().strftime("%A, %d %B %Y"),
    )


class Chatbot:
    def __init__(self, provider_name: str | None = None) -> None:
        name = provider_name or default_provider()

        if name is None:
            raise ProviderError(
                "No API key found. Add at least one key to your .env file."
            )

        self.provider: BaseProvider
        self.provider_name: str
        self.set_provider(name)
        self.reset()

    def set_provider(self, name: str) -> None:
        """Switch AI provider. The conversation history is kept."""
        self.provider = create_provider(name)
        self.provider_name = name

    def reset(self) -> None:
        self.messages = [
            {
                "role": "system",
                "content": build_system_prompt(),
            }
        ]

    def reply(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        try:
            answer = self.provider.chat(self.messages)
        except Exception:
            # Remove the failed user message from memory.
            self.messages.pop()
            raise

        self.messages.append({"role": "assistant", "content": answer})

        return answer
