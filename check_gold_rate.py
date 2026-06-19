import os
import re
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SITE_URL = "https://ravijewellers.lk/"
STATE_FILE = "rate.json"

def send_msg(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=30
    )
    print("Telegram:", r.status_code, r.text)
    r.raise_for_status()

html = requests.get(
    SITE_URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
).text

soup = BeautifulSoup(html, "html.parser")
text = soup.get_text(" ", strip=True)

print(text[:1500])

matches = re.findall(r"22\s*KT\s*LKR\s*([0-9,]+)", text, re.I)

if not matches:
    send_msg("⚠️ Ravi Gold Alert error: could not find 22KT rate on website.")
    raise Exception("Could not find 22KT rate")

# Ravi page contains old rates also, so take the last/current one
rate = matches[-1]

try:
    with open(STATE_FILE, "r") as f:
        old = json.load(f).get("rate", "")
except:
    old = ""

if old == "":
    send_msg(f"✅ Ravi Gold Alert started\nCurrent 22KT: LKR {rate}")
elif rate != old:
    send_msg(
        f"🔔 Ravi Jewellers Gold Rate Changed\n\n"
        f"Old 22KT: LKR {old}\n"
        f"New 22KT: LKR {rate}\n"
        f"{SITE_URL}"
    )
else:
    print(f"No change. Current 22KT: LKR {rate}")

with open(STATE_FILE, "w") as f:
    json.dump({"rate": rate}, f)
