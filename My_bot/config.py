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

DB_PATH = "godje_club.db"