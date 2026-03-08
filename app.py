import os
import re
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- Environment setup ---
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# --- LLM setup (created once, reused for all requests) ---
llm = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Joking AI. Give me only ONE funny joke on the given topic."),
    ("user", "generate a joke on the topic: {topic}")
])

chain = prompt | llm | StrOutputParser()

# --- Rate limiting (per user, 10 second cooldown) ---
MAX_TOPIC_LENGTH = 50
RATE_LIMIT_SECONDS = 10
user_last_request: dict[int, float] = {}

JOKE_CATEGORIES = [
    "programming", "python", "javascript", "AI", "science",
    "math", "history", "animals", "food", "sports",
    "movies", "music", "technology", "school", "work"
]


def is_rate_limited(user_id: int) -> bool:
    """Check if a user is rate limited. Returns True if they should be blocked."""
    now = time.time()
    last = user_last_request.get(user_id, 0)
    if now - last < RATE_LIMIT_SECONDS:
        return True
    user_last_request[user_id] = now
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm a joke bot powered by AI.\n\n"
        "Here's how to use me:\n"
        "• /joke <topic> — Get a joke on any topic\n"
        "• /categories — See suggested topics\n"
        "• /help — Show this message again\n\n"
        "In DMs, just type a topic and I'll generate a joke!\n"
        "In groups, mention me like @JokeEngine_Bot python"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **How to get jokes:**\n\n"
        "• /joke <topic> — Get a joke (e.g. /joke python)\n"
        "• /categories — Browse topic suggestions\n"
        "• In DMs: just type any topic directly\n"
        "• In groups: mention me with @JokeEngine_Bot <topic>\n\n"
        "One joke every 10 seconds per user.",
        parse_mode="Markdown"
    )


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topics = ", ".join(JOKE_CATEGORIES)
    await update.message.reply_text(
        f"📋 **Suggested joke topics:**\n\n{topics}\n\n"
        "Use /joke <topic> or just type a topic in DMs!",
        parse_mode="Markdown"
    )


async def generate_joke(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    user_id = update.effective_user.id

    # Rate limiting
    if is_rate_limited(user_id):
        await update.message.reply_text("⏳ Slow down! Please wait 10 seconds between jokes.")
        return

    # Input sanitization
    topic = topic.strip()
    if len(topic) > MAX_TOPIC_LENGTH:
        await update.message.reply_text(f"📏 Topic is too long! Please keep it under {MAX_TOPIC_LENGTH} characters.")
        return

    if not topic:
        await update.message.reply_text("Please specify a topic! e.g. /joke python")
        return

    # Typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        joke = (await chain.ainvoke({"topic": topic})).strip()
        await update.message.reply_text(joke)
    except Exception:
        await update.message.reply_text("😔 Sorry, I couldn't generate a joke right now. Please try again later.")


async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else ""
    if not topic:
        await update.message.reply_text("Usage: /joke <topic>\nExample: /joke python")
        return
    await generate_joke(update, context, topic)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if not msg:
        return

    bot_username = context.bot.username
    chat_type = update.effective_chat.type

    # In private chats (DMs), treat the entire message as a topic
    if chat_type == "private":
        await generate_joke(update, context, msg.strip())
        return

    # In group chats, only respond to mentions
    if f'@{bot_username}' in msg:
        match = re.search(rf'@{re.escape(bot_username)}\s+(.*)', msg)
        if match and match.group(1).strip():
            await generate_joke(update, context, match.group(1).strip())
        else:
            await update.message.reply_text("Please specify a topic after mentioning me!")


def main():
    token = os.getenv("TELEGRAM_API_KEY")
    if not token:
        raise ValueError("TELEGRAM_API_KEY environment variable is not set")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("joke", joke_command))
    app.add_handler(CommandHandler("categories", categories_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()