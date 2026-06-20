import os
import re
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SITE_URL = "https://ravijewellers.lk/"
STATE_FILE = "rate.json"

def send_message(message):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message},
        timeout=30
    )
    print("Telegram:", r.status_code, r.text)
    r.raise_for_status()

html = requests.get(
    SITE_URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
).text

text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

print(text[:2000])

matches = re.findall(r"22\s*KT\s*LKR\s*([0-9,]+)", text, re.I)

if not matches:
    matches = re.findall(r"22KT\s+LKR\s+([0-9,]+)", text, re.I)

if not matches:
    send_message("⚠️ Ravi Gold Alert: Cannot find 22KT rate. Website text changed.")
    raise Exception("22KT rate not found")

current_rate = matches[-1]

try:
    with open(STATE_FILE, "r") as f:
        old_rate = json.load(f).get("rate", "")
except:
    old_rate = ""

if old_rate and current_rate != old_rate:
    old_num = int(old_rate.replace(",", ""))
    new_num = int(current_rate.replace(",", ""))

    if new_num > old_num:
        change = f"Increased 📈 by LKR {new_num - old_num:,}"
    else:
        change = f"Decreased 📉 by LKR {old_num - new_num:,}"

    send_message(
        f"🔔 Ravi Jewellers Gold Rate Changed\n\n"
        f"Old 22KT: LKR {old_rate}\n"
        f"New 22KT: LKR {current_rate}\n"
        f"{change}\n\n"
        f"{SITE_URL}"
    )

elif not old_rate:
    send_message(f"✅ Ravi Gold Alert started\nCurrent 22KT: LKR {current_rate}")

with open(STATE_FILE, "w") as f:
    json.dump({"rate": current_rate}, f)
