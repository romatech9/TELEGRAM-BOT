import requests
from telegram import Update
from telegram.ext import ContextTypes

async def currency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /currency 100000 UGX to USD
    if len(context.args) < 4 or "to" not in context.args:
        await update.message.reply_text("Usage: `/currency 100000 UGX to USD`", parse_mode='Markdown')
        return
    
    try:
        amount = float(context.args[0])
        from_currency = context.args[1].upper()
        to_currency = context.args[3].upper()
        
        await update.message.reply_text(f"💱 Converting {amount} {from_currency} to {to_currency}...")
        
        # Free API, no key needed
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        rate = data["rates"][to_currency]
        result = amount * rate
        
        await update.message.reply_text(
            f"**{amount:,.2f} {from_currency} = {result:,.2f} {to_currency}**\n"
            f"Rate: 1 {from_currency} = {rate:.4f} {to_currency}",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text("❌ Invalid format or currency code. Example: `/currency 50 USD to UGX`", parse_mode='Markdown')