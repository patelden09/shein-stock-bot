import time
import requests
import os
import json
import re
import random
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

CHECK_INTERVAL = 60        # base check interval
ALERT_COOLDOWN = 900       # 15 minutes

# ==========================================

bot = Bot(token=BOT_TOKEN)
last_alert = {}

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.shein.com/",
    "Connection": "keep-alive"
})

def check_stock(product_id):
    url = f"https://www.shein.com/product-p-{product_id}.html"

    r = SESSION.get(url, timeout=20)
    html = r.text

    # Try multiple patterns (Shein changes often)
    patterns = [
        r'window\.__INIT_STATE__\s*=\s*({.*?});',
        r'window\.__PRELOADED_STATE__\s*=\s*({.*?});'
    ]

    data = None
    for pattern in patterns:
        match = re.search(pattern, html, re.S)
        if match:
            data = json.loads(match.group(1))
            break

    if not data:
        raise Exception("Product data not found")

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

            # random delay between products (VERY IMPORTANT)
            time.sleep(random.uniform(3, 6))

        except Exception as e:
            print(f"Error checking {pid}: {e}")

    # wait before next full cycle
    time.sleep(CHECK_INTERVAL + random.uniform(10, 25))
