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

        # نضيف نفس الـ headers اللي يرسلها المتصفح
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Origin": "https://omanreal.com",
            "Referer": "https://omanreal.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",

            # ⚠️ هنا لازم تحطي الكوكيز اللي نسختيها من المتصفح كاملة
            "Cookie": "bi=aYB4YWRAS65MJBtnLSqS6%2BJ4OXkSp2X%2BC97cXwp3n5s%3D; nltm=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6ImRjYzdjMzNkLTExZjItNGVmMi1hYjVjLWFjZGQ4ZjE3YThmOSIsImp0aSI6Im9qRTUwdiIsInJvbGUiOiJBbm9ueW1vdXMiLCJ1c2VyX2ludGVybmFsX2lkIjoiODI3MDg3OTIiLCJuYmYiOjE3NTgxNjg1NDksImV4cCI6MTc2ODUzNjU0OSwiaWF0IjoxNzU4MTY4NTQ5LCJpc3MiOiJPbWFuIFJlYWwifQ.IIu0MuDH0QqKP1Y-hY4Ed0FFabs5n8ydIHBsyl7R8eY; _ga=GA1.1.941230911.1758168550; _ga_WEDBP3L8G9=GS2.1.s1758193792$o6$g1$t1758193811$j41$l0$h0"
        }

        # POST مع body فاضي (زي ما يطلب الـ API)
        resp = requests.post(API_URL, headers=headers, json={}, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        listings = data.get("items", [])
        send_message(f"ℹ️ API returned {len(listings)} items")

        # Debug: نرسل أول إعلان كـ raw JSON للتأكد
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
    send_message("✅ Bot started via API (TEST MODE: POST request with headers)")
    while True:
        check_new_properties()
        time.sleep(30)

# ✅ نشغل البوت مباشرة
t = threading.Thread(target=run_bot, daemon=True)
t.start()

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
