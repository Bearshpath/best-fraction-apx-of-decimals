
from telethon import TelegramClient, events
import os
from flask import Flask
import threading
import asyncio

def best_rational(x, N):
    if x < 0:
        num, denom = best_rational(-x, N)
        return -num, denom
    elif x < 1:
        return farey(x, N)
    else:
        k = int(x)
        f = x - k
        if f == 0:
            return k, 1
        else:
            n, d = farey(f, N)
            return (k * d + n, d)

def farey(x, N):
    a, b = 0, 1
    c, d = 1, 1
    while b <= N and d <= N:
        mediant = (a + c) / (b + d)
        if x == mediant:
            if (b + d) <= N:
                return a + c, b + d
            elif d > b:
                return c, d
            else:
                return a, b
        elif x > mediant:
            a, b = a + c, b + d
        else:
            c, d = a + c, b + d
    return (c, d) if b > N else (a, b)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def main():
    api_id = '29677891'  # Get this from my.telegram.org
    api_hash = '3f53f1dba0f255b941c64f9e3b97137a'  # Get this from my.telegram.org
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        return

    client = TelegramClient('bot_session', api_id, api_hash)
    await client.start(bot_token=bot_token)

    @client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        await event.reply("Hello! I'm a bot that helps with rational approximations.\nUse /approx <number> <max_denominator> to get started.")

    @client.on(events.NewMessage(pattern='/approx'))
    async def handle_approx(event):
        try:
            args = event.text.split()[1:]
            if len(args) != 2:
                await event.reply("Usage: /approx <number> <max_denom>")
                return

            number = float(args[0])
            max_denom = int(args[1])
            
            if max_denom <= 0:
                await event.reply("Maximum denominator must be positive")
                return

            num, denom = best_rational(number, max_denom)
            approx_value = num / denom
            error = abs(number - approx_value)

            response = f"Best rational approximation for {number} (max denom={max_denom}):\n{num}/{denom} = {approx_value}\nError: {error}"
            await event.reply(response)
        except Exception as e:
            await event.reply(f"Error: {str(e)}")

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("Bot started. Press Ctrl+C to stop.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
