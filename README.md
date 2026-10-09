# Nexora — AI Assistant with Live Web Search

A clean, dark-themed chat assistant built with Streamlit. It can answer questions,
write and explain code, and **search the web in real time** (DuckDuckGo), citing its sources.

## Features
- Multiple AI providers in one app: **Hugging Face**, **Groq**, **Google Gemini**
- Switch provider from the sidebar without losing the conversation
- Live web search with clickable source links
- Export any chat as a Markdown file
- Friendly error messages (bad key, wrong model, rate limit)
- Terminal mode (`main.py`) as well as the web UI

## Quick start

```bash
# 1. (recommended) create a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # macOS / Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. add your API key(s)
copy .env.example .env          # Windows   (macOS/Linux: cp .env.example .env)
# open .env and paste at least ONE key

# 4. run the web app
streamlit run app.py
```

Terminal version: `python main.py --provider groq`

## Getting an API key (you only need one)

| Provider | Variable in `.env` | Where to create the key |
|---|---|---|
| Groq (fast, free tier) | `GROQ_API_KEY` | https://console.groq.com/keys |
| Google Gemini (free tier) | `GEMINI_API_KEY` | https://aistudio.google.com/apikey |
| Hugging Face | `HF_TOKEN` | https://huggingface.co/settings/tokens |

Providers that have a key appear automatically in the sidebar. Model names change
often; if you see "model not found", set `GROQ_MODEL` / `GEMINI_MODEL` / `HF_MODEL`
in `.env` to a current model from that provider's documentation.

## Project structure

```
app.py                       Streamlit interface
chatbot.py                   Conversation memory + system prompt
config.py                    Branding, providers, .env loading
main.py                      Terminal version
providers/
  base.py                    Tool-calling loop, retries, friendly errors
  huggingface_provider.py    Hugging Face client
  openai_compatible.py       Groq + Gemini (OpenAI-compatible APIs)
tools/web_search.py          DuckDuckGo search tool
.streamlit/config.toml       Dark theme colours
```

## Customising
- **Name:** set `APP_NAME` in `.env` (or edit `config.py`).
- **Colours:** `.streamlit/config.toml` and the `STYLE` block in `app.py`.
- **Add another provider:** add an entry to `PROVIDERS` in `config.py`
  (any OpenAI-compatible service works with `openai_compatible.py`).

## Security
Never commit your `.env` file or paste API keys into the code. `.env` is already
listed in `.gitignore`. If a key is ever exposed, delete it in the provider's
dashboard and create a new one.

## Deploying
On Streamlit Community Cloud, add the same variables under **Settings → Secrets**
(e.g. `GROQ_API_KEY = "..."`) instead of uploading a `.env` file.
