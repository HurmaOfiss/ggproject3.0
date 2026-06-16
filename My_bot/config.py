import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

TARIFFS_PHOTO_PATH = "цены.jpg"
EQUIPMENT_PHOTOS = [
    "гарнитура1.jpg",
    "гарнитура2.jpg",
    "гарнитура3.jpg",
    "гарнитура4.jpg",
    "гарнитура5.jpg"
]

# База данных будет лежать в подпапке data/
DB_PATH = "data/godje_club.db"

# Уведомления: за сколько минут до начала отправлять напоминание
NOTIFY_MINUTES = 60