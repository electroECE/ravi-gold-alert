import os
import re
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://ravijewellers.lk/"
RATE_FILE = "rate.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

    print(response.text)

html = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"}
).text

soup = BeautifulSoup(html, "html.parser")
text = soup.get_text(" ", strip=True)

print(text)

matches = re.findall(r"22KT\s*LKR\s*([0-9,]+)", text)

if not matches:
    raise Exception("Gold rate not found")

current_rate = matches[-1]

try:
    with open(RATE_FILE, "r") as f:
        old_rate = json.load(f)["rate"]
except:
    old_rate = ""

if old_rate == "":
    send_telegram(
        f"✅ Ravi Gold Alert Started\n\nCurrent 22KT Rate: LKR {current_rate}"
    )

elif current_rate != old_rate:

    old_num = int(old_rate.replace(",", ""))
    new_num = int(current_rate.replace(",", ""))

    if new_num > old_num:
        status = f"📈 Increased by LKR {new_num-old_num:,}"
    else:
        status = f"📉 Decreased by LKR {old_num-new_num:,}"

    send_telegram(
        f"🔔 Ravi Gold Rate Changed\n\n"
        f"Old Rate: LKR {old_rate}\n"
        f"New Rate: LKR {current_rate}\n\n"
        f"{status}"
    )

with open(RATE_FILE, "w") as f:
    json.dump({"rate": current_rate}, f)
