import os
import telebot
import cloudscraper
from flask import Flask
from threading import Thread

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Mini serveur web local
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(func=lambda message: True)
def search_vinted(message):
    query = message.text
    bot.reply_to(message, f"🔍 Recherche en cours pour : *{query}*...", parse_mode="Markdown")
    
    try:
        scraper = cloudscraper.create_scraper()
        
        url = f"https://www.vinted.fr/api/v2/catalog/items?search_text={query}&per_page=3&order=newest_first"
        
        # Requête directe via la connexion locale de ton téléphone
        response = scraper.get(url, timeout=10)
        
        if response.status_code != 200:
            bot.reply_to(message, f"❌ Échec (Code {response.status_code}). Vinted ou Cloudflare a bloqué la requête.")
            return

        data = response.json()
        items = data.get("items", [])
        
        if not items:
            bot.reply_to(message, "Aucun article trouvé.")
            return
            
        result_text = f"🔥 **Succès ! Résultats pour : {query}** :\n\n"
        for item in items:
            title = item.get("title", "Sans titre")
            price = item.get("price", "N/C")
            currency = item.get("currency", "€")
            link = f"https://www.vinted.fr/items/{item.get('id')}"
            result_text += f"▪️ **{title}**\n💰 {price} {currency}\n🔗 [Voir]({link})\n\n"
            
        bot.reply_to(message, result_text, parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur de connexion avec Vinted : {e}")

if __name__ == "__main__":
    # Lance le serveur web en arrière-plan
    t = Thread(target=run_flask)
    t.start()
    # Lance le bot Telegram
    bot.infinity_polling()

