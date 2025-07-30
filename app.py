import requests

# Telegram Bot Configuration
BOT_TOKEN = '7613703350:AAGIvRqgsG_yTcOlFADRSYd_FtoLOPwXDKk'
CHAT_ID = '-1002840229810'
MESSAGE_TEXT = """
📈 *Aayeshatech Astro Trend | Nifty & Bank Nifty (July 31, 2025)* 📉

*Key Astro Observations:*
1. **Moon shifts from Virgo (Mercury) to Libra (Venus) at 11:04 AM** – Volatility expected.
2. **Jupiter Retrograde at 1:26 PM** – Possible trend reversal.
3. **Venus in Gemini (Mercury-ruled)** – Speculative moves likely.

*Market Outlook (9:15 AM - 3:30 PM IST):*
- *9:15-11:04 AM*: Sideways-to-bearish (Chitra + Jupiter retro shadow).
- *11:04 AM*: Bullish shift (Moon enters Libra).
- *1:26 PM*: Bearish risk (Jupiter retro exact).
- *After 1:30 PM*: Avoid aggressive longs.

*Bank Nifty*: More volatile, strong swings possible.

*Final Remark*: Trade cautiously post 1:30 PM.
"""

# Send to Telegram
def send_telegram_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

# Execute
if __name__ == "__main__":
    result = send_telegram_message(BOT_TOKEN, CHAT_ID, MESSAGE_TEXT)
    print("Message sent successfully!" if result.get("ok") else "Failed to send message.")
