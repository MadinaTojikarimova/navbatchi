import os
import asyncio
import logging
import sys
import psycopg2
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_RAW = os.getenv("CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate environment variables early with clear errors
if not TOKEN:
    logging.error("Missing BOT_TOKEN environment variable")
    sys.exit("Missing BOT_TOKEN environment variable")

if CHAT_ID_RAW is None:
    logging.error("Missing CHAT_ID environment variable")
    sys.exit("Missing CHAT_ID environment variable")
try:
    CHAT_ID = int(CHAT_ID_RAW)
except ValueError:
    logging.error("CHAT_ID must be an integer: %s", CHAT_ID_RAW)
    sys.exit("CHAT_ID must be an integer")

if not DATABASE_URL:
    logging.error("Missing DATABASE_URL environment variable")
    sys.exit("Missing DATABASE_URL environment variable")

bot = Bot(TOKEN)
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

# PostgreSQL connection with error handling
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
except Exception as e:
    logging.exception("Failed to connect to the database")
    sys.exit(f"Database connection failed: {e}")

# Table yaratish (agar mavjud bo‘lmasa)
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    week_index INTEGER
)
""")
conn.commit()

# Agar qiymat yo'q bo'lsa 0 qilib qo'yamiz
cursor.execute("SELECT week_index FROM settings WHERE id=1")
row = cursor.fetchone()

if row is None:
    cursor.execute("INSERT INTO settings (id, week_index) VALUES (1, 0)")
    conn.commit()
    week_index = 0
else:
    week_index = row[0]

duty_list = [
    "Mubina, @mubinafinance",
    "Madina, @utkirjonovna7",
    "Zarina @luchik_o8, Mohina @mokhinabotirova1020",
    "Oydinoy",
    "Nilufar, @N1lufarsl8",
    "Shohidil @abduvalievaash, Marhabo @htmvnass",
    "Karomatoy, @ksultanovaa"
]

async def send_duty():
    global week_index
    name = duty_list[week_index]

    message = f"""
Bismillahir Rohmanir Rohiym

📅 Tozalik navbati

👤 Navbatchi: {name}

📍 Tozalanadigan joylar:
- Hall (chotkalash va supurish)
- Oshxona
- Hammom va hojatxona
- paketlarni olib chiqish
- Iloji bo'lsa, podyezdni ham supurish

✨ Tozalik iymonning yarmi
"""
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception:
        logging.exception("Failed to send duty message to chat_id=%s", CHAT_ID)
        return

    # Keyingi hafta
    week_index = (week_index + 1) % len(duty_list)
    try:
        cursor.execute("UPDATE settings SET week_index=%s WHERE id=1", (week_index,))
        conn.commit()
    except Exception:
        logging.exception("Failed to update week_index in database")

async def main():
    scheduler.add_job(
        send_duty,
        trigger='cron',
        day_of_week='sat',
        hour=20,
        minute=10
    )
    scheduler.start()
    await asyncio.sleep(float('inf'))

asyncio.run(main())