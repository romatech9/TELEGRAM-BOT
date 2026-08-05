import requests
from telegram import Update
from telegram.ext import ContextTypes

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Default city is Iganga. You can do /weather Kampala to change it
    city = " ".join(context.args) if context.args else "Iganga"
    
    await update.message.reply_text(f"🌤️ Fetching weather for {city}...")
    
    try:
        # Using wttr.in - no API key needed, works instantly
        url = f"https://wttr.in/{city}?format=4"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            weather = response.text.strip()
            await update.message.reply_text(f"📍 {weather}")
        else:
            await update.message.reply_text("Sorry, couldn't get weather for that city 😅")
            
    except Exception as e:
        await update.message.reply_text("Weather service is down. Try again later.")