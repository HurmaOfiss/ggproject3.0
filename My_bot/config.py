import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

TARIFFS_PHOTO_PATH = "prices.jpg"
EQUIPMENT_PHOTOS = [
    "headset1.jpg",
    "headset2.jpg",
    "headset3.jpg",
    "headset4.jpg",
    "headset5.jpg"
]

DB_PATH = "data/godje_club.db"

NOTIFY_MINUTES = 60