import os
import sys
import logging
import asyncio
import psycopg2
from telegram import Bot

logging.basicConfig(level=logging.INFO)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_RAW = os.getenv("CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate environment variables
if not TOKEN:
    logging.error("Missing BOT_TOKEN environment variable")
    sys.exit("Missing BOT_TOKEN environment variable")

if not CHAT_ID_RAW:
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

# Initialize bot
bot = Bot(TOKEN)

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
except Exception as e:
    logging.exception("Failed to connect to the database")
    sys.exit(f"Database connection failed: {e}")

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    week_index INTEGER
)
""")
conn.commit()

# Initialize week_index
cursor.execute("SELECT week_index FROM settings WHERE id=1")
row = cursor.fetchone()
if row is None:
    cursor.execute("INSERT INTO settings (id, week_index) VALUES (1, 0)")
    conn.commit()
    week_index = 0
else:
    week_index = row[0]

# Duty list
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
        logging.info("Duty message sent successfully")
    except Exception:
        logging.exception("Failed to send duty message to chat_id=%s", CHAT_ID)
        return

    # Update week_index
    week_index = (week_index + 1) % len(duty_list)
    try:
        cursor.execute("UPDATE settings SET week_index=%s WHERE id=1", (week_index,))
        conn.commit()
        logging.info("Week index updated to %s", week_index)
    except Exception:
        logging.exception("Failed to update week_index in database")

async def main():
    await send_duty()  # Run once and exit

if __name__ == "__main__":
    asyncio.run(main())