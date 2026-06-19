import os
import re
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

url = "https://ravijewellers.lk/"

html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")
text = soup.get_text()

match = re.search(r'22KT.*?LKR\s*([\d,]+)', text, re.I)

if match:
    rate = match.group(1)

    try:
        with open("rate.json", "r") as f:
            old = json.load(f)["rate"]
    except:
        old = ""

    if rate != old:

        msg = f"🔔 Ravi Jewellers Gold Rate Changed\n\nNew Rate: LKR {rate}"

        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": msg
            }
        )

        with open("rate.json", "w") as f:
            json.dump({"rate": rate}, f)
