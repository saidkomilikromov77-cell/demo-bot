import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ===== TOKENNI SHU YERGA YOZING =====
BOT_TOKEN = "8956803432:AAFSYDN7giVDzM6EQMEAxgoh1uG8WJV0cx8"

# ===== ADMIN ID (buyurtmalar keladigan chat) =====
# O'z Telegram ID ingizni bilish uchun @userinfobot ga /start yuboring
ADMIN_ID = 6306395011  # <-- o'zgartiring

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Mahsulotlar ro'yxati ---
MENU = {
    "🍕 Pizza Margarita": "25,000 so'm",
    "🍔 Burger Classic": "30,000 so'm",
    "🥗 Salat Cezar": "20,000 so'm",
    "🧃 Limonad": "10,000 so'm",
}

# --- FSM holatlari ---
class OrderState(StatesGroup):
    choosing = State()
    confirm = State()

class AppointmentState(StatesGroup):
    name = State()
    phone = State()
    time = State()

# --- Asosiy menyu ---
def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Menyu"), KeyboardButton(text="🛒 Buyurtma")],
            [KeyboardButton(text="📅 Navbat olish"), KeyboardButton(text="📞 Aloqa")],
        ],
        resize_keyboard=True
    )

# --- /start ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"Salom, {message.from_user.first_name}! 👋\n\n"
        "Bizning botga xush kelibsiz!\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=main_keyboard()
    )

# --- Menyu ---
@dp.message(F.text == "📋 Menyu")
async def show_menu(message: types.Message):
    text = "📋 *Bizning menyu:*\n\n"
    for item, price in MENU.items():
        text += f"{item} — {price}\n"
    text += "\nBuyurtma berish uchun 🛒 *Buyurtma* tugmasini bosing!"
    await message.answer(text, parse_mode="Markdown")

# --- Buyurtma ---
@dp.message(F.text == "🛒 Buyurtma")
async def order_start(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=item)] for item in MENU.keys()] +
                 [[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True
    )
    await message.answer("Nima buyurtma qilmoqchisiz?", reply_markup=keyboard)
    await state.set_state(OrderState.choosing)

@dp.message(OrderState.choosing)
async def order_chosen(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("Asosiy menyu:", reply_markup=main_keyboard())
        return

    if message.text not in MENU:
        await message.answer("Iltimos, menyudan tanlang!")
        return

    await state.update_data(item=message.text, price=MENU[message.text])
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Tasdiqlash"), KeyboardButton(text="❌ Bekor")]],
        resize_keyboard=True
    )
    await message.answer(
        f"Siz tanladingiz:\n{message.text} — {MENU[message.text]}\n\nTasdiqlaysizmi?",
        reply_markup=keyboard
    )
    await state.set_state(OrderState.confirm)

@dp.message(OrderState.confirm)
async def order_confirm(message: types.Message, state: FSMContext):
    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        await message.answer(
            f"✅ Buyurtmangiz qabul qilindi!\n\n"
            f"📦 {data['item']} — {data['price']}\n\n"
            "Tez orada siz bilan bog'lanamiz! 😊",
            reply_markup=main_keyboard()
        )
        await bot.send_message(
            ADMIN_ID,
            f"🛒 *Yangi buyurtma!*\n\n"
            f"👤 {message.from_user.full_name} (@{message.from_user.username})\n"
            f"📦 {data['item']} — {data['price']}",
            parse_mode="Markdown"
        )
    else:
        await message.answer("Buyurtma bekor qilindi.", reply_markup=main_keyboard())
    await state.clear()

# --- Navbat olish ---
@dp.message(F.text == "📅 Navbat olish")
async def appointment_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Navbat olish uchun ismingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AppointmentState.name)

@dp.message(AppointmentState.name)
async def appointment_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(AppointmentState.phone)

@dp.message(AppointmentState.phone)
async def appointment_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="10:00"), KeyboardButton(text="12:00")],
            [KeyboardButton(text="14:00"), KeyboardButton(text="16:00")],
            [KeyboardButton(text="18:00")],
        ],
        resize_keyboard=True
    )
    await message.answer("Qaysi vaqt qulay?", reply_markup=keyboard)
    await state.set_state(AppointmentState.time)

@dp.message(AppointmentState.time)
async def appointment_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f"✅ Navbat band qilindi!\n\n"
        f"👤 Ism: {data['name']}\n"
        f"📞 Tel: {data['phone']}\n"
        f"🕐 Vaqt: {message.text}\n\n"
        "Siz bilan bog'lanamiz! 😊",
        reply_markup=main_keyboard()
    )
    await bot.send_message(
        ADMIN_ID,
        f"📅 *Yangi navbat!*\n\n"
        f"👤 {data['name']}\n"
        f"📞 {data['phone']}\n"
        f"🕐 {message.text}",
        parse_mode="Markdown"
    )
    await state.clear()

# --- Aloqa ---
@dp.message(F.text == "📞 Aloqa")
async def contact(message: types.Message):
    await message.answer(
        "📞 *Biz bilan bog'laning:*\n\n"
        "📱 Telefon: +998 90 123 45 67\n"
        "📍 Manzil: Toshkent, Chilonzor\n"
        "🕐 Ish vaqti: 9:00 — 21:00\n"
        "📩 Telegram: @sizning_username",
        parse_mode="Markdown"
    )

# --- Ishga tushurish ---
async def main():
    print("Bot ishga tushdi! ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
