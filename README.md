# JokeEngine Bot

A Telegram bot that generates AI-powered jokes on any topic using OpenAI GPT-OSS 20B (via Groq) and LangChain.

## Features

- `/joke <topic>` - Generate a joke on any topic
- `/categories` - Browse suggested joke topics
- **DM support** - Just type a topic in a private chat
- **Group support** - Mention `@Binary_Joke_Bot <topic>` in groups
- **Rate limiting** - 1 joke per 10 seconds per user
- **Input sanitization** - Topics capped at 50 characters

## Prerequisites

- Python 3.10+
- A Telegram Bot token from [@BotFather](https://t.me/BotFather)
- A Groq API key from [console.groq.com](https://console.groq.com)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Senthuran-dev/Telegram-Bot.git
   cd Telegram-Bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your API keys:
   ```
   TELEGRAM_API_KEY=your_telegram_bot_token
   GROQ_API_KEY=your_groq_api_key
   ```

4. **Run the bot**
   ```bash
   python app.py
   ```

## Deployment (Vercel Serverless Webhook)

This repository is configured to be deployed as a serverless function on Vercel.

1. Create a new project on [Vercel](https://vercel.com/) and connect your GitHub repository.
2. In the Vercel project settings, add the following Environment Variables:
   - `TELEGRAM_API_KEY`
   - `GROQ_API_KEY`
3. Deploy the project.
4. Once deployed, register your Vercel URL with Telegram by visiting this URL in your browser (replace with your actual token and Vercel URL):
   `https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/setWebhook?url=https://<YOUR_VERCEL_APP>.vercel.app/api/webhook`

## Tech Stack

- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- [LangChain](https://www.langchain.com/) - LLM orchestration
- [Groq](https://groq.com/) - Fast LLM inference