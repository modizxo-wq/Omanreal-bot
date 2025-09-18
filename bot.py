import os
import time
import threading
import requests
from flask import Flask

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://api.omanreal.com/api/Listing/GetListingsAndClusters?includeMapMarkers=true"

sent_ids = set()

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ OmanReal API Bot is running!"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        resp = requests.post(url, data=data, timeout=15)
        resp.raise_for_status()
        print(f"📨 Sent Telegram message: {text[:50]}...")
    except Exception as e:
        print("❌ Error sending message to Telegram:", e)

def check_new_properties():
    global sent_ids
    try:
        send_message("🔍 Checking new properties...")

        headers = {"Content-Type": "application/json"}
        # POST request with empty body
        resp = requests.post(API_URL, headers=headers, json={}, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        listings = data.get("items", [])
        send_message(f"ℹ️ API returned {len(listings)} items")

        # Debug: أرسل أول إعلان كـ JSON للتأكد
        if listings:
            first_item = listings[0]
            send_message(f"📝 First item raw data:\n{str(first_item)[:500]}")

        # مؤقت: نرسل أول 3 إعلانات فقط
        for item in listings[:3]:
            item_id = item.get("id")
            slug = item.get("slug")
            title = item.get("title", "Unknown")
            price = item.get("price", "Not mentioned")
            addresses = " / ".join([a["title"] for a in item.get("address", [])])
            size = " / ".join([f"{f['value']} {f['item']}" for f in item.get("featureSnippets", [])]) or "Not specified"
            link = f"https://omanreal.com/p/{slug}"

            if item_id in sent_ids:
                continue

            msg = (
                f"🏠 {title}\n"
                f"📍 Location: {addresses}\n"
                f"💰 Price: {price} R.O\n"
                f"📏 Size: {size}\n"
                f"🔗 Link: {link}"
            )
            send_message(msg)
            send_message(f"✅ Sent TEST property: {title} | {addresses} | {price} R.O")

            sent_ids.add(item_id)

    except Exception as e:
        send_message(f"❌ Error fetching API listings: {e}")

def run_bot():
    send_message("🚀 Thread started: Bot will check every 30 seconds")
    send_message("✅ Bot started via API (TEST MODE: POST request)")
    while True:
        check_new_properties()
        time.sleep(30)

# ✅ نشغل البوت مباشرة
t = threading.Thread(target=run_bot, daemon=True)
t.start()

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
