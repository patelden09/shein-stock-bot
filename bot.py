import time
import requests
import os
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PRODUCT_IDS = [
    "443318501001", "443323021006", "443332092007",
    "443330229001", "443317440006", "443326096013",
    "443336505003", "443381716011", "443336681001",
    "443381755001", "443386967012", "443381954007",
    "443381633007", "443381954012", "443332287006"
]

SIZES = ["XXL", "38"]
CHECK_INTERVAL = 60        # check every 1 minute
ALERT_COOLDOWN = 900       # 15 minutes

bot = Bot(token=BOT_TOKEN)
last_alert = {}

def check_stock(product_id):
    url = f"https://api.shein.com/product/detail?goods_id={product_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    for sku in data.get("info", {}).get("skus", []):
        if sku.get("attr_value") in SIZES and sku.get("stock", 0) > 0:
            return True
    return False

while True:
    for pid in PRODUCT_IDS:
        try:
            in_stock = check_stock(pid)
            now = time.time()

            if in_stock and now - last_alert.get(pid, 0) > ALERT_COOLDOWN:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🟢 IN STOCK!\nProduct ID: {pid}\nSizes: XXL / 38"
                )
                last_alert[pid] = now

        except Exception as e:
            print(f"Error checking {pid}: {e}")

    time.sleep(CHECK_INTERVAL)
