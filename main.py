import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ----------------------------
# Rational Approximation Code
# ----------------------------

def farey(x, N):
    """
    Given 0 < x < 1, find the best rational approximation using mediants
    with denominator no larger than N.
    """
    a, b = 0, 1  # Lower bound: 0/1
    c, d = 1, 1  # Upper bound: 1/1
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
            a, b = a + c, b + d  # Update lower bound
        else:
            c, d = a + c, b + d  # Update upper bound
    return (c, d) if b > N else (a, b)

def best_rational(x, N):
    """
    Return the best rational approximation to a positive number x
    with denominator no larger than N.
    """
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

# ----------------------------
# Telegram Bot Code
# ----------------------------

async def approx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /approx command.
    Expected format: /approx <number> <max_denom>
    """
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Usage: /approx <number> <max_denom>")
            return
        number = float(args[0])
        max_denom = int(args[1])
        if max_denom <= 0:
            await update.message.reply_text("Maximum denominator must be a positive integer.")
            return

        num, denom = best_rational(number, max_denom)
        approx_value = num / denom
        error = abs(number - approx_value)
        response = (
            f"Best rational approximation for {number} (denom <= {max_denom}):\n"
            f"{num}/{denom} = {approx_value}\n"
            f"Absolute error: {error}"
        )
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ----------------------------
# Flask Web Server (Keep-Alive)
# ----------------------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ----------------------------
# Main Function to Start the Bot
# ----------------------------

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token is None:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        return

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("approx", approx_command))

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Bot is running. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
