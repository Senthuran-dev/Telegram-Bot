import os
import sys

# Add the project root to the path so we can import app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from telegram import Update
from app import get_bot

# FastAPI application instance
app = FastAPI()

# Telegram bot instance
ptb_app = get_bot()

# We use this to ensure the Telegram app is initialized only once
is_initialized = False

@app.post("/api/webhook")
async def webhook(request: Request):
    """
    Handle incoming Telegram webhooks.
    """
    global is_initialized

    # Initialize the PTB application if it hasn't been already
    if not is_initialized:
        await ptb_app.initialize()
        is_initialized = True

    # Parse the incoming JSON into a Telegram Update object
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)

    # Process the update using our Telegram handlers
    await ptb_app.process_update(update)

    return {"status": "ok"}
