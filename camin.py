import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus
from datetime import datetime, timedelta
import pytz
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

TOKEN = "8120850189:AAE2fvg-eqmRwHaGvfIznwEvOOAG6ZQUvIc"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 📅 Дата начала отсчёта дежурств
START_DATE = datetime(2025, 9, 1)

# 💾 Список всех чатов, куда бот отправляет (будет автоматически пополняться)
known_chats = set()

# 📌 Добавлен в новую группу
@dp.chat_member()
async def on_added(event: ChatMemberUpdated):
    if event.new_chat_member.status == ChatMemberStatus.MEMBER:
        chat_id = event.chat.id
        known_chats.add(chat_id)
        print(f"✅ Бот добавлен в группу: {event.chat.title} ({chat_id})")

# 🔢 Получить номер комнаты от 01 до 21
def get_room_number(today: datetime) -> str:
    current = START_DATE
    count = 0
    while current.date() < today.date():
        if current.weekday() in [0, 1, 2, 3]:  # ПН–ЧТ
            count += 1
        current += timedelta(days=1)
    room_num = (count % 21) + 1
    return f"{room_num:02d}"

async def send_reminders():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(120)  # Ждём 2 минуты
    
    now = datetime.now(pytz.timezone("Europe/Chisinau"))
    date_str = now.strftime("%d.%m.%Y")
    weekday_str = {
        0: "понедельник",
        1: "вторник",
        2: "среда",
        3: "четверг",
        4: "пятница",
        5: "суббота",
        6: "воскресенье"
    }[now.weekday()]
    room = get_room_number(now)
    message = (
        f"🧼 Сегодня {date_str} ({weekday_str})\n"
        f"Комната {room} — уборка кухни в 22:00"
    )
    for chat_id in known_chats:
        try:
            await bot.send_message(chat_id, message)
            print(f"📨 Отправлено в {chat_id}: комната {room}")
        except Exception as e:
            print(f"❌ Ошибка в {chat_id}: {e}")

# 🌐 Простой HTTP сервер для поддержки хоста (Render, Railway)
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"I'm alive!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('', port), DummyHandler)
    server.serve_forever()

# 🚀 Точка входа
async def main():
    print("🚀 Бот запущен")
    asyncio.create_task(send_reminders())
    await dp.start_polling()

if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    asyncio.run(main())
