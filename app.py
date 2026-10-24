import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import telebot

# --- Le serveur HTTP pour valider le port Render ---
def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serveur HTTP démarré sur le port {port}")
    httpd.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# --- Le Bot Telegram ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salut ! Le sniper Vinted est en ligne 🚀")

print("Le bot Telegram démarre...")
bot.infinity_polling()
