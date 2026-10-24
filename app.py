import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import telebot
import requests

# --- 1. Le serveur HTTP pour valider le port Render (obligatoire) ---
def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serveur HTTP démarré sur le port {port}")
    httpd.serve_forever()

# Lancement du serveur en arrière-plan
threading.Thread(target=run_http_server, daemon=True).start()

# --- 2. Ton Bot Telegram & Logique de Sniper ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salut ! 🚀 Envoie-moi un mot-clé (ex: Airmax, PS4, Sweat...) et je cherche les derniers articles sur Vinted pour toi !")

# Gestion des messages texte (Recherche Vinted avec Session pour contourner les protections)
@bot.message_handler(func=lambda message: True)
def search_vinted(message):
    query = message.text
    bot.reply_to(message, f"🔍 Recherche en cours pour : *{query}*...", parse_mode="Markdown")
    
    try:
        # Création d'une session pour imiter un vrai navigateur
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Accept": "application/json, text/plain, */*"
        }
        
        # Étape 1 : Visiter la page d'accueil pour récupérer les cookies de session
        session.get("https://www.vinted.fr", headers=headers, timeout=10)
        
        # Étape 2 : Interroger l'API avec la session active
        url = f"https://www.vinted.fr/api/v2/catalog/items?search_text={query}&per_page=3"
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            bot.reply_to(message, f"❌ Vinted a bloqué la requête (Code {response.status_code}).")
            return

        data = response.json()
        items = data.get("items", [])
        
        if not items:
            bot.reply_to(message, "Aucun article trouvé pour cette recherche.")
            return
            
        # Formater et envoyer les résultats
        result_text = f"✨ **Top 3 des résultats pour : {query}** :\n\n"
        for item in items:
            title = item.get("title", "Sans titre")
            price = item.get("price", "N/C")
            currency = item.get("currency", "€")
            item_id = item.get("id")
            link = f"https://www.vinted.fr/items/{item_id}"
            
            result_text += f"▪️ **{title}**\n💰 Prix : {price} {currency}\n🔗 [Voir l'annonce]({link})\n\n"
            
        bot.reply_to(message, result_text, parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Oups, une erreur technique est survenue.")

print("Le bot Telegram démarre...")
bot.infinity_polling()
