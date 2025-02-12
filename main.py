import os
from telegram.ext import Updater, CommandHandler
import threading
from flask import Flask

def approx_command(update, context):
    try:
        args = context.args
        if len(args) != 2:
            update.message.reply_text("Usage: /approx <number> <max_denom>")
            return
        number = float(args[0])
        max_denom = int(args[1])
        if max_denom <= 0:
            update.message.reply_text("Maximum denominator must be positive")
            return

        num, denom = best_rational(number, max_denom)
        approx_value = num / denom
        error = abs(number - approx_value)

        response = f"Best rational approximation for {number} (max denom={max_denom}):\n{num}/{denom} = {approx_value}\nError: {error}"
        update.message.reply_text(response)
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

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

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        return

    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("approx", approx_command))

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("Bot started. Press Ctrl+C to stop.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()