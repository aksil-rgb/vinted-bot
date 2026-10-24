import os
import telebot
import cloudscraper

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def search_vinted(message):
    query = message.text
    bot.reply_to(message, f"🔍 Test du proxy pour : *{query}*...", parse_mode="Markdown")
    
    try:
        scraper = cloudscraper.create_scraper()
        
        # ⚠️ C'est ici qu'on met l'IP et le port du proxy gratuit
        proxies = {
            'https': 'http://195.154.191.26:1099'
        }
        
        url = f"https://www.vinted.fr/api/v2/catalog/items?search_text={query}&per_page=3&order=newest_first"
        
        # On passe le proxy à la requête
        response = scraper.get(url, proxies=proxies, timeout=10)
        
        if response.status_code != 200:
            bot.reply_to(message, f"❌ Échec (Code {response.status_code}). Le proxy est mort ou bloqué par Cloudflare.")
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
        bot.reply_to(message, f"❌ Erreur de connexion : le proxy ne répond pas.")
