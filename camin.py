import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus
from datetime import datetime, timedelta
import pytz

# 🔐 Твой токен:
TOKEN = "8120850189:AAE2fvg-eqmRwHaGvfIznwEvOOAG6ZQUvIc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🧾 Дата начала дежурств:
START_DATE = datetime(2025, 9, 1)

# Группы этажей: подставишь свои ID ниже после добавления бота в группы
group_floor_map = {
    -1000000000001: 2,  # ID группы этажа 2
    -1000000000002: 3,  # ID группы этажа 3
    -1000000000003: 4,  # ID группы этажа 4
    -1000000000004: 5,  # ID группы этажа 5
}

# Когда бот добавляется в новую группу — автоматически запоминаем её
@dp.chat_member()
async def on_added_to_group(event: ChatMemberUpdated):
    if event.new_chat_member.status == ChatMemberStatus.MEMBER:
        chat_id = event.chat.id
        print(f"✅ Бот добавлен в группу: {event.chat.title} ({chat_id})")
        # ❗ Добавь вручную соответствие этажу (2, 3, 4, 5)
        # Пример: group_floor_map[chat_id] = 3

# 🧼 Функция определения номера дежурной комнаты
def get_room_number(floor: int, today: datetime) -> int:
    current = START_DATE
    count = 0
    while current.date() < today.date():
        if current.weekday() in [0, 1, 2, 3]:  # ПН-ЧТ
            count += 1
        current += timedelta(days=1)
    offset = count % 21
    return floor * 100 + 1 + offset

# 📤 Отправка напоминаний
async def send_reminders():
    await bot.delete_webhook(drop_pending_updates=True)
    while True:
        now = datetime.now(pytz.timezone("Europe/Chisinau"))
        if now.weekday() in [0, 1, 2, 3] and now.hour == 22 and now.minute == 0:
            date_str = now.strftime("%d.%m.%Y")
            weekday_str = {
                0: "понедельник",
                1: "вторник",
                2: "среда",
                3: "четверг"
            }[now.weekday()]
            for chat_id, floor in group_floor_map.items():
                room_number = get_room_number(floor, now)
                message = (
                    f"🧼 Сегодня {date_str} ({weekday_str})\n"
                    f"Комната {room_number} — уборка кухни в 22:00"
                )
                try:
                    await bot.send_message(chat_id, message)
                    print(f"📨 Отправлено в {chat_id}: комната {room_number}")
                except Exception as e:
                    print(f"❌ Ошибка в {chat_id}: {e}")
            await asyncio.sleep(60)  # Ждём минуту, чтобы не дублировал
        await asyncio.sleep(10)

async def main():
    print("🚀 Бот запущен")
    await dp.start_polling(bot)

# 🔁 Запуск
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(send_reminders())
    loop.run_until_complete(main())
