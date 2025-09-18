import os
import time
import threading
import requests
from flask import Flask

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://api.omanreal.com/api/Listing/GetListingsAndClusters?includeMapMarkers=true"

TARGET_LOCATIONS = ["muscat", "al amrat", "barka", "yiti"]
SPECIAL_BARKA = ["fuleij", "al fuleij", "fuleij al maamura", "al fuleij al maamoura"]

sent_ids = set()

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ OmanReal API Bot is running!"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❌ Error sending message:", e)

def check_new_properties():
    global sent_ids
    try:
        print("🔍 Checking new properties...")
        resp = requests.get(API_URL, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        listings = data.get("items", [])
        print(f"ℹ️ API returned {len(listings)} items")

        for item in listings:
            item_id = item.get("id")
            slug = item.get("slug")
            title = item.get("title", "Unknown")
            price = item.get("price", "Not mentioned")
            addresses = " / ".join([a["title"] for a in item.get("address", [])])
            size = " / ".join([f'{f["value"]} {f["item"]}' for f in item.get("featureSnippets", [])]) or "Not specified"
            link = f"https://omanreal.com/p/{slug}"

            # Skip if already sent
            if item_id in sent_ids:
                print(f"⏩ Skipping (already sent): {title}")
                continue

            # فلترة: Residential فقط
            if "residential" not in title.lower():
                print(f"⏩ Skipping (not residential): {title}")
                continue

            # فلترة: الموقع
            loc_lower = addresses.lower()
            if not any(loc in loc_lower for loc in TARGET_LOCATIONS):
                print(f"⏩ Skipping (location not in target): {addresses}")
                continue

            # فلترة خاصة ببركا
            if "barka" in loc_lower:
                if not any(keyword in loc_lower for keyword in SPECIAL_BARKA):
                    print(f"⏩ Skipping (Barka but not Fuleij): {addresses}")
                    continue

            msg = (
                f"🏠 {title}\n"
                f"📍 Location: {addresses}\n"
                f"💰 Price: {price} R.O\n"
                f"📏 Size: {size}\n"
                f"🔗 Link: {link}"
            )
            send_message(msg)
            print(f"✅ Sent property: {title} | {addresses} | {price} R.O")

            sent_ids.add(item_id)

    except Exception as e:
        print("❌ Error fetching API listings:", e)

def run_bot():
    send_message("✅ Bot started via API (every 30 sec for testing)")
    print("🚀 Bot started, will check every 30 seconds (testing mode)")
    while True:
        check_new_properties()
        time.sleep(30)  # ⏳ بدل 600 ثانية

# ✅ خلي الـ thread يشتغل مباشرة
t = threading.Thread(target=run_bot, daemon=True)
t.start()

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

