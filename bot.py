import asyncio
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

TOKEN = "7747731785:AAF9gE1jS9PkltwUdHacW5JG6cNcQITkLsE"
CHAT_ID = -5244694657

bot = Bot(TOKEN)
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

# Navbatchilar (tartib bo'yicha)
duty_list = ["Madina", "Oydinoy","Shohidil", "Karomatoy",
             "Zarina", "Mohina", "Nilufar", "Mubina"]

week_index = 0 

async def send_duty():
    global week_index
    name = duty_list[week_index]

    message = f"""
 Bismillahir Rohmanir Rohiym

📅 Shanba kechki tozalik navbati (TEST)

👤 Navbatchi: {name}

📍  Tozalanadigan joylar:
- Hall (chotkalash va supurish)
- Oshxona
- Hammom va hojatxona
- paketlarni olib chiqish
- Iloji bo'lsa, podyezdni ham supurish

✨ Tozalik iymonning yarmi

Diqqat jarima: Vaqtida tozalamagan navbatchi podyezdlarni supurish va paketlarni olib chiqish vazifasini bajarishi kerak bo'ladi.
"""

    await bot.send_message(chat_id=CHAT_ID, text=message)
    week_index = (week_index + 1) % len(duty_list)

# Hozirgi vaqtdan 2 daqiqadan keyin ishlash
run_time = datetime.now() + timedelta(minutes=2)

async def main():
    scheduler.add_job(send_duty, 'date', run_date=run_time)
    scheduler.start()
    # Keep the bot running
    await asyncio.sleep(float('inf'))

# Botni run qilish
asyncio.run(main())