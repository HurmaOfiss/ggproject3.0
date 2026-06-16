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

# База данных будет лежать в подпапке data/
DB_PATH = "data/godje_club.db"

# Уведомления: за сколько минут до начала отправлять напоминание
NOTIFY_MINUTES = 60