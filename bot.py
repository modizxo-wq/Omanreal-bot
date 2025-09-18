import os
import time
import requests

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Error sending message:", e)

if __name__ == "__main__":
    send_message("✅ Bot started and running on Railway!")
    while True:
        time.sleep(60)  
        send_message("⏰ Still running...")
