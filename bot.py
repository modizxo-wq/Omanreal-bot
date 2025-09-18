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
TARGET_LOCATIONS = ["Muscat", "Al Amrat", "Barka", "Yiti"]
# Only accept Barka if it includes Fuleij
SPECIAL_BARKA = ["Fuleij", "Al Fuleij", "Fuleij Al Maamura", "Al Fuleij Al Maamoura"]

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
            price = card.find("span", class_="price").get_text(strip=True) if card.find("span", class_="price") else "Not mentioned"
            title = card.find("div", class_="property-type").get_text(strip=True) if card.find("div", class_="property-type") else "Unknown"
            location = card.find("div", class_="location").get_text(strip=True) if card.find("div", class_="location") else "Unknown"
            size = card.find("div", class_="area").get_text(strip=True) if card.find("div", class_="area") else "Not specified"
            link = "https://omanreal.com" + card.find("a")["href"]

            # Skip if already sent
            if link in sent_links:
                continue

            # Filter: only Residential
            if "Residential" not in title:
                continue

            # Filter: location must match
            if not any(loc in location for loc in TARGET_LOCATIONS):
                continue

            # Extra filter for Barka
            if "Barka" in location:
                if not any(keyword in location for keyword in SPECIAL_BARKA):
                    continue

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

