import time
import requests
import os
import json
import re
from telegram import Bot

# ================= CONFIG =================

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
ALERT_COOLDOWN = 900       # alert once every 15 minutes per product

# ==========================================

bot = Bot(token=BOT_TOKEN)
last_alert = {}

def check_stock(product_id):
    url = f"https://www.shein.com/product-p-{product_id}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    r = requests.get(url, headers=headers, timeout=15)
    html = r.text

    match = re.search(r'window\.__INIT_STATE__\s*=\s*({.*?});', html, re.S)
    if not match:
        raise Exception("Product data not found")

    data = json.loads(match.group(1))
    skus = (
        data.get("goods", {})
        .get("goodsDetail", {})
        .get("skuInfo", {})
        .get("skuList", [])
    )

    for sku in skus:
        size = sku.get("attrValue", "")
        stock = sku.get("stock", 0)

        if size in SIZES and stock > 0:
            return True

    return False


print("🟢 Bot started. Monitoring products...")

while True:
    for pid in PRODUCT_IDS:
        try:
            in_stock = check_stock(pid)
            now = time.time()

            if in_stock and now - last_alert.get(pid, 0) > ALERT_COOLDOWN:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=(
                        "🟢 IN STOCK!\n"
                        f"Product ID: {pid}\n"
                        "Sizes: XXL / 38\n"
                        f"Link: https://www.shein.com/product-p-{pid}.html"
                    )
                )
                last_alert[pid] = now

        except Exception as e:
            print(f"Error checking {pid}: {e}")

    time.sleep(CHECK_INTERVAL)
