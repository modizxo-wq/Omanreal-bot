import os
import time
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://omanreal.com/p"

# Allowed locations
TARGET_LOCATIONS = ["muscat", "al amrat", "barka", "yiti"]
# Only accept Barka if it includes Fuleij
SPECIAL_BARKA = ["fuleij", "al fuleij", "fuleij al maamura", "al fuleij al maamoura"]

# Keep track of already sent links
sent_links = set()

# Flask app (لازم عشان Render ما يعطي Error)
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ OmanReal Bot is running!"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Error sending message:", e)

def check_new_properties():
    global sent_links
    try:
        r = requests.get(BASE_URL, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.find_all("div", class_="property-item")

        for card in cards:
            link = "https://omanreal.com" + card.find("a")["href"]

            # Skip if already sent
            if link in sent_links:
                continue

            # افتح صفحة التفاصيل
            try:
                detail = requests.get(link, timeout=15)
                detail_soup = BeautifulSoup(detail.text, "html.parser")

                title = detail_soup.find("h1", class_="font-weight-bold h4").get_text(" ", strip=True)
                location = detail_soup.find("h2", class_="mb-2 font-weight-normal h5").get_text(strip=True)
                price = detail_soup.find("h2", class_="font-weight-normal").get_text(strip=True)
                size_tag = detail_soup.find("p", class_="mb-2 text-muted")
                size = size_tag.get_text(strip=True) if size_tag else "Not specified"

            except Exception as e:
                print("Error scraping detail page:", e)
                continue

            # فلترة النوع
            if "Residential" not in title:
                continue

            # فلترة الموقع (case-insensitive)
            loc_lower = location.lower()
            if not any(loc in loc_lower for loc in TARGET_LOCATIONS):
                continue

            # فلترة خاصة لـ Barka
            if "barka" in loc_lower:
                if not any(keyword in loc_lower for keyword in SPECIAL_BARKA):
                    continue

            # إرسال التفاصيل
            msg = (
                f"🏠 {title}\n"
                f"📍 Location: {location}\n"
                f"💰 Price: {price}\n"
                f"📏 Size: {size}\n"
                f"🔗 Link: {link}"
            )
            send_message(msg)

            # Mark as sent
            sent_links.add(link)

    except Exception as e:
        print("Error checking properties:", e)

def run_bot():
    send_message("✅ Bot started and running (every 10 min)")
    while True:
        check_new_properties()
        time.sleep(600)  # every 10 minutes

if __name__ == "__main__":
    # نشغل البوت في Thread
    t = threading.Thread(target=run_bot)
    t.start()

    # نشغل Flask على البورت اللي يطلبه Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

