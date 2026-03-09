import os
import requests
import time
import uuid
import random
from datetime import datetime

# ===== НАСТРОЙКИ =====
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {int(os.getenv("ADMIN_ID", "0")), 713129783}
SUPPORT = "GiftExchangersSupport"
MANAGER = "GiftExchangersManager"
BOT_USERNAME = "GiftExchagersBot"

# ===== ДАННЫЕ =====
deals = {}
top_deals = []
users = {}
banned_users = set()

user_states = {}
user_temp = {}

settings = {
    "banner_text": (
        "👋 Приветствуем в проекте «Gift Exchange».\n\n"
        "🤝 Наш проект создан для безопасных обменов Telegram подарков между пользователями.\n\n"
        "👇 Для взаимодействия с ботом, нажмите одну из кнопок ниже:"
    )
}

CURRENCIES = ["💵 USD", "💶 EUR", "🇷🇺 RUB", "🇺🇦 UAH", "🇰🇿 KZT", "₿ BTC", "💎 ETH", "🔷 USDT", "🪙 TON"]

MENU_BUTTONS = {
    "📝 Создать сделку",
    "❓ Как происходит сделка",
    "ℹ️ Информация",
    "📞 Техподдержка",
    "🏆 Топ-15 обменов",
    "/start",
    "/admin",
}

# ===== УТИЛИТЫ =====
def tg(method, data):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    try:
        r = requests.post(url, json=data, timeout=10)
        return r.json()
    except Exception as e:
        print(f"[tg error] {method}: {e}")
        return None

def answer_cb(cid, text=None):
    d = {"callback_query_id": cid}
    if text:
        d["text"] = text
    tg("answerCallbackQuery", d)

def send(chat_id, text, markup=None):
    d = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if markup:
        d["reply_markup"] = markup
    return tg("sendMessage", d)

def send_inline(chat_id, text, buttons):
    return send(chat_id, text, {"inline_keyboard": buttons})

def edit(chat_id, msg_id, text, buttons=None):
    d = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        d["reply_markup"] = {"inline_keyboard": buttons}
    return tg("editMessageText", d)

def delete(chat_id, msg_id):
    tg("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})

def mask(username):
    name = username.lstrip("@")
    if len(name) <= 3:
        return f"@{name[0]}***"
    return f"@{name[:2]}***{name[-2:]}"

def deal_link(deal_id):
    return f"https://t.me/{BOT_USERNAME}?start=d{deal_id}"

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ===== КЛАВИАТУРЫ =====
def kb_main():
    return {
        "keyboard": [
            [{"text": "📝 Создать сделку"}],
            [{"text": "❓ Как происходит сделка"}, {"text": "ℹ️ Информация"}],
            [{"text": "📞 Техподдержка"}, {"text": "🏆 Топ-15 обменов"}],
        ],
        "resize_keyboard": True,
    }

def kb_admin():
    return [
        [{"text": "📊 Статистика", "callback_data": "a_stats"}],
        [{"text": "📢 Рассылка", "callback_data": "a_broadcast"}],
        [{"text": "🚫 Бан", "callback_data": "a_ban"}, {"text": "✅ Разбан", "callback_data": "a_unban"}],
        [{"text": "📝 Баннер", "callback_data": "a_banner"}],
        [{"text": "📋 Сделки", "callback_data": "a_deals"}],
        [{"text": "🔄 Обновить топ", "callback_data": "a_top"}],
        [{"text": "❌ Закрыть", "callback_data": "a_close"}],
    ]

def kb_currencies():
    rows = []
    for i in range(0, len(CURRENCIES), 3):
        row = []
        for cur in CURRENCIES[i:i+3]:
            row.append({"text": cur, "callback_data": f"currency_{cur}"})
        rows.append(row)
    rows.append([{"text": "❌ Отмена", "callback_data": "cancel_deal"}])
    return rows

# ===== ТОП-15 =====
def generate_top():
    names = ["Alex", "Bob", "Carl", "Dan", "Eve", "Frank", "Grace", "Henry",
             "Ivan", "Jack", "Kate", "Leo", "Mia", "Nick", "Olga"]
    result = []
    for _ in range(15):
        u1 = random.choice(names) + str(random.randint(10, 99))
        u2 = random.choice(names) + str(random.randint(10, 99))
        amount = random.randint(50, 1000)
        cur = random.choice(["USD", "USDT", "RUB", "TON", "ETH"])
        result.append({"user1": f"@{u1}", "user2": f"@{u2}", "amount": amount, "currency": cur})
    result.sort(key=lambda x: x["amount"], reverse=True)
    return result

# ===== СБРОС СОСТОЯНИЯ =====
def reset_state(user_id):
    user_states.pop(user_id, None)
    user_temp.pop(user_id, None)

# ===== ТЕКСТ СДЕЛКИ С ИНСТРУКЦИЕЙ =====
def deal_text_full(deal, deal_id):
    my_nft = deal.get("my_nft", "—")
    his_nft = deal.get("his_nft", "—")
    amount = deal["amount"]
    currency = deal["currency"]
    creator = deal["creator_name"]
    second = deal["second_user"]

    return (
        f"✅ <b>СДЕЛКА СОЗДАНА!</b>\n\n"
        f"🆔 <b>Номер:</b> <code>{deal_id}</code>\n"
        f"👤 <b>Создатель:</b> @{creator}\n"
        f"👤 <b>Участник:</b> @{second}\n"
        f"💰 <b>Сумма:</b> {amount} {currency}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎁 <b>NFT создателя:</b> {my_nft}\n"
        f"🎁 <b>NFT участника:</b> {his_nft}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>ЧТО НУЖНО СДЕЛАТЬ:</b>\n\n"
        f"🔴 <b>@{creator} (создатель)</b> — передайте вашу NFT менеджеру:\n"
        f"     👉 <b>@{MANAGER}</b>\n\n"
        f"🔵 <b>@{second} (участник)</b> — ожидайте подтверждения от менеджера,\n"
        f"     затем передайте свою NFT менеджеру:\n"
        f"     👉 <b>@{MANAGER}</b>\n\n"
        f"⚠️ <b>Не передавайте NFT напрямую!</b> Только через @{MANAGER}\n"
        f"⏱ Время обмена: <b>5–15 минут</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>Ссылка для участника:</b>\n"
        f"{deal_link(deal_id)}"
    )

def deal_info_text(deal, deal_id):
    status_map = {
        "waiting": "⏳ Ожидает принятия",
        "in_progress": "🔄 В процессе",
        "cancelled": "❌ Отменена",
        "completed": "✅ Завершена",
    }
    my_nft = deal.get("my_nft", "—")
    his_nft = deal.get("his_nft", "—")
    creator = deal["creator_name"]
    second = deal["second_user"]
    return (
        f"🔍 <b>СДЕЛКА #{deal_id}</b>\n\n"
        f"👤 <b>Создатель:</b> @{creator}\n"
        f"👤 <b>Участник:</b> @{second}\n"
        f"💰 <b>Сумма:</b> {deal['amount']} {deal['currency']}\n"
        f"📊 <b>Статус:</b> {status_map.get(deal['status'], deal['status'])}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎁 <b>NFT создателя:</b> {my_nft}\n"
        f"🎁 <b>NFT участника:</b> {his_nft}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>ЧТО НУЖНО СДЕЛАТЬ:</b>\n\n"
        f"🔴 <b>@{creator} (создатель)</b> — передайте вашу NFT менеджеру:\n"
        f"     👉 <b>@{MANAGER}</b>\n\n"
        f"🔵 <b>@{second} (участник)</b> — после подтверждения от менеджера\n"
        f"     передайте свою NFT менеджеру:\n"
        f"     👉 <b>@{MANAGER}</b>\n\n"
        f"⚠️ Только через <b>@{MANAGER}</b>, не напрямую!\n"
        f"⏱ Время: <b>5–15 минут</b>"
    )

# ===== ОБРАБОТКА СООБЩЕНИЙ =====
def handle_message(message):
    global top_deals

    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    user_id = message["from"]["id"]
    username = message["from"].get("username", "NoUsername")
    first_name = message["from"].get("first_name", "Пользователь")

    if user_id in banned_users:
        send(chat_id, "🚫 Вы забанены в боте!")
        return

    users[user_id] = {"username": username, "first_name": first_name, "chat_id": chat_id}

    if text in MENU_BUTTONS or text.startswith("/start"):
        reset_state(user_id)

    state = user_states.get(user_id)

    # ===== СОСТОЯНИЯ СОЗДАНИЯ СДЕЛКИ =====
    if state == "wait_username":
        second_user = text.lstrip("@").strip()
        if not second_user or " " in second_user:
            send(chat_id, "<b>❌ Введите корректный @username (без пробелов):</b>")
            return
        user_temp[user_id]["second_user"] = second_user
        user_states[user_id] = "wait_my_nft"
        send(chat_id, "<b>Введите ссылку на ВАШУ NFT (которую отдаёте):</b>")
        return

    if state == "wait_my_nft":
        user_temp[user_id]["my_nft"] = text
        user_states[user_id] = "wait_his_nft"
        send(chat_id, "<b>Введите ссылку на ЕГО NFT (которую получаете):</b>")
        return

    if state == "wait_his_nft":
        user_temp[user_id]["his_nft"] = text
        user_states[user_id] = "wait_currency"
        send_inline(chat_id, "<b>💱 Выберите валюту сделки:</b>", kb_currencies())
        return

    if state == "wait_amount":
        raw = text.replace(",", ".").replace(" ", "")
        try:
            amount = float(raw)
            if amount <= 0:
                send(chat_id, "<b>❌ Сумма должна быть больше нуля. Введите ещё раз:</b>")
                return
        except ValueError:
            send(chat_id, "<b>❌ Введите число, например: 150 или 0.5</b>")
            return
        currency = user_temp[user_id].get("currency", "USD")
        _create_deal(chat_id, user_id, username, amount, currency)
        return

    # ===== СОСТОЯНИЯ АДМИНА =====
    if state == "a_broadcast" and is_admin(user_id):
        reset_state(user_id)
        sent = 0
        for uid, ud in users.items():
            if uid not in ADMIN_IDS:
                try:
                    send(ud["chat_id"], f"<b>📢 Сообщение от администратора:</b>\n\n{text}")
                    sent += 1
                    time.sleep(0.05)
                except:
                    pass
        send(chat_id, f"<b>✅ Рассылка отправлена: {sent} пользователям</b>")
        return

    if state == "a_ban" and is_admin(user_id):
        reset_state(user_id)
        target = text.lstrip("@").strip()
        found = False
        for uid, ud in users.items():
            if ud.get("username", "").lower() == target.lower() or str(uid) == target:
                banned_users.add(uid)
                send(chat_id, f"<b>✅ @{target} забанен</b>")
                found = True
                break
        if not found:
            send(chat_id, "<b>❌ Пользователь не найден</b>")
        return

    if state == "a_unban" and is_admin(user_id):
        reset_state(user_id)
        target = text.lstrip("@").strip()
        found = False
        for uid in list(banned_users):
            ud = users.get(uid, {})
            if ud.get("username", "").lower() == target.lower() or str(uid) == target:
                banned_users.discard(uid)
                send(chat_id, f"<b>✅ @{target} разбанен</b>")
                found = True
                break
        if not found:
            send(chat_id, "<b>❌ Пользователь не найден в бан-листе</b>")
        return

    if state == "a_banner" and is_admin(user_id):
        reset_state(user_id)
        settings["banner_text"] = text
        send(chat_id, f"<b>✅ Баннер обновлён!</b>\n\n{text}")
        return

    # ===== КОМАНДЫ И КНОПКИ =====
    if text == "/start":
        send(chat_id, settings["banner_text"], kb_main())
        return

    if text.startswith("/start d"):
        deal_id = text[8:].strip()
        _show_deal(chat_id, user_id, username, deal_id)
        return

    if text == "/admin" and is_admin(user_id):
        t = (
            f"<b>👨‍💼 ПАНЕЛЬ АДМИНИСТРАТОРА</b>\n\n"
            f"<b>📊 Сделок:</b> {len(deals)}\n"
            f"<b>👥 Пользователей:</b> {len(users)}\n"
            f"<b>🚫 Забанено:</b> {len(banned_users)}"
        )
        send_inline(chat_id, t, kb_admin())
        return

    if text == "📝 Создать сделку":
        user_states[user_id] = "wait_username"
        user_temp[user_id] = {}
        send(chat_id, "<b>Введите @username второго участника сделки:</b>")
        return

    if text == "❓ Как происходит сделка":
        t = (
            "<b>❓ Как происходит сделка в Gift Exchange?</b>\n\n"
            "• Участники договариваются об условиях 🤝\n"
            "• Один создаёт сделку через бота 🎁\n"
            "• Второй получает ссылку и открывает сделку 📤\n"
            f"• Создатель передаёт NFT менеджеру @{MANAGER} 💰\n"
            "• Менеджер одобряет ✔️\n"
            f"• Участник передаёт свою NFT менеджеру @{MANAGER} 📦\n"
            "• Менеджер передаёт NFT первому 🔄\n"
            "• Сделка завершена! ✅"
        )
        send_inline(chat_id, t, [[{"text": "🏠 Главное меню", "callback_data": "main_menu"}]])
        return

    if text == "ℹ️ Информация":
        t = (
            "<b>📤 Gift Exchange — безопасный обмен NFT-подарками в Telegram.</b>\n\n"
            "<b>Плюсы проекта:</b>\n"
            "• Быстрые и безопасные обмены\n"
            "• Техподдержка 24/7\n"
            "• Гарантия каждой сделки\n"
            "• Конфиденциальность данных\n\n"
            f"<b>📞 Менеджер:</b> @{MANAGER}"
        )
        send_inline(chat_id, t, [
            [{"text": "❓ Как происходит сделка", "callback_data": "how_deal"}],
            [{"text": "🏠 Главное меню", "callback_data": "main_menu"}],
        ])
        return

    if text == "📞 Техподдержка":
        send(chat_id,
             f"<b>📞 Техническая поддержка:</b>\n\n"
             f"<b>👤 Поддержка:</b> @{SUPPORT}\n"
             f"<b>👤 Менеджер:</b> @{MANAGER}\n\n"
             "<b>Напишите им в личные сообщения!</b>",
             kb_main())
        return

    if text == "🏆 Топ-15 обменов":
        if not top_deals:
            top_deals = generate_top()
        lines = "<b>🏆 ТОП-15 ЛУЧШИХ ОБМЕНОВ</b>\n\n"
        for i, d in enumerate(top_deals[:15], 1):
            lines += f"<b>{i}.</b> {mask(d['user1'])} ↔ {mask(d['user2'])} — {d['amount']} {d['currency']}\n"
        send(chat_id, lines, kb_main())
        return

# ===== СОЗДАНИЕ СДЕЛКИ (без подтверждения) =====
def _create_deal(chat_id, user_id, username, amount, currency):
    global top_deals

    deal_id = str(uuid.uuid4())[:8]
    temp = user_temp.get(user_id, {})
    second_user = temp.get("second_user", "")
    my_nft = temp.get("my_nft", "")
    his_nft = temp.get("his_nft", "")

    deals[deal_id] = {
        "creator_id": user_id,
        "creator_name": username,
        "second_user": second_user,
        "my_nft": my_nft,
        "his_nft": his_nft,
        "amount": amount,
        "currency": currency,
        "status": "in_progress",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "participant_id": None,
    }

    reset_state(user_id)

    # Добавляем в топ
    top_deals.append({
        "user1": f"@{username}",
        "user2": f"@{second_user}",
        "amount": amount,
        "currency": currency,
    })
    top_deals = sorted(top_deals, key=lambda x: x["amount"], reverse=True)[:15]

    t = deal_text_full(deals[deal_id], deal_id)
    buttons = [
        [{"text": "💬 Написать менеджеру", "url": f"https://t.me/{MANAGER}"}],
        [{"text": "🏠 В меню", "callback_data": "main_menu"}],
    ]
    send_inline(chat_id, t, buttons)

    # Уведомляем второго участника если он уже в боте
    for uid, ud in users.items():
        if ud.get("username", "").lower() == second_user.lower():
            notify = (
                f"<b>🔔 Вас приглашают к обмену!</b>\n\n"
                f"<b>@{username} создал сделку с вами</b>\n\n"
                f"🆔 <b>Номер:</b> <code>{deal_id}</code>\n"
                f"💰 <b>Сумма:</b> {amount} {currency}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 <b>Что нужно сделать:</b>\n\n"
                f"🔵 <b>Вы (участник)</b> — после того как создатель передаст NFT,\n"
                f"     передайте свою NFT менеджеру:\n"
                f"     👉 <b>@{MANAGER}</b>\n\n"
                f"⚠️ Только через менеджера, не напрямую!\n\n"
                f"🔗 <b>Открыть сделку:</b> {deal_link(deal_id)}"
            )
            send_inline(ud["chat_id"], notify, [
                [{"text": "💬 Написать менеджеру", "url": f"https://t.me/{MANAGER}"}],
            ])
            break

    # Уведомляем всех админов
    admin_notify = (
        f"🆕 <b>Новая сделка!</b>\n\n"
        f"🆔 <code>{deal_id}</code>\n"
        f"👤 Создатель: @{username} | ID: <code>{user_id}</code>\n"
        f"👤 Участник: @{second_user}\n"
        f"🎁 NFT создателя: {my_nft}\n"
        f"🎁 NFT участника: {his_nft}\n"
        f"💰 Сумма: {amount} {currency}\n"
        f"📅 {deals[deal_id]['created_at']}"
    )
    for admin_id in ADMIN_IDS:
        ad = users.get(admin_id, {})
        if ad.get("chat_id"):
            send(ad["chat_id"], admin_notify)

def _show_deal(chat_id, user_id, username, deal_id):
    if deal_id not in deals:
        send(chat_id, "<b>❌ Сделка не найдена!</b>", kb_main())
        return
    deal = deals[deal_id]
    t = deal_info_text(deal, deal_id)
    buttons = [
        [{"text": "💬 Написать менеджеру", "url": f"https://t.me/{MANAGER}"}],
        [{"text": "🏠 В меню", "callback_data": "main_menu"}],
    ]
    send_inline(chat_id, t, buttons)

# ===== ОБРАБОТКА CALLBACK =====
def handle_callback(callback):
    global top_deals

    cid = callback["id"]
    chat_id = callback["message"]["chat"]["id"]
    msg_id = callback["message"]["message_id"]
    data = callback["data"]
    user_id = callback["from"]["id"]
    username = callback["from"].get("username", "NoUsername")

    answer_cb(cid)

    if data.startswith("currency_"):
        if user_states.get(user_id) != "wait_currency":
            return
        currency = data[len("currency_"):]
        user_temp[user_id]["currency"] = currency
        user_states[user_id] = "wait_amount"
        edit(chat_id, msg_id,
             f"<b>Валюта выбрана: {currency}</b>\n\n<b>Введите сумму сделки (например: 150 или 0.5):</b>")
        return

    if data == "cancel_deal":
        reset_state(user_id)
        delete(chat_id, msg_id)
        send(chat_id, "<b>❌ Создание сделки отменено.</b>", kb_main())
        return

    if data == "main_menu":
        delete(chat_id, msg_id)
        send(chat_id, settings["banner_text"], kb_main())
        return

    if data == "how_deal":
        t = (
            "<b>❓ Как происходит сделка в Gift Exchange?</b>\n\n"
            "• Участники договариваются об условиях 🤝\n"
            "• Один создаёт сделку через бота 🎁\n"
            "• Второй получает ссылку и открывает сделку 📤\n"
            f"• Создатель передаёт NFT менеджеру @{MANAGER} 💰\n"
            "• Менеджер одобряет ✔️\n"
            f"• Участник передаёт свою NFT менеджеру @{MANAGER} 📦\n"
            "• Менеджер передаёт NFT первому 🔄\n"
            "• Сделка завершена! ✅"
        )
        edit(chat_id, msg_id, t, [[{"text": "🏠 Главное меню", "callback_data": "main_menu"}]])
        return

    # ===== ADMIN CALLBACKS =====
    if not is_admin(user_id):
        return

    if data == "a_stats":
        t = (
            f"<b>📊 СТАТИСТИКА</b>\n\n"
            f"Всего сделок: {len(deals)}\n"
            f"⏳ Ожидают: {sum(1 for d in deals.values() if d['status']=='waiting')}\n"
            f"🔄 В процессе: {sum(1 for d in deals.values() if d['status']=='in_progress')}\n"
            f"✅ Завершено: {sum(1 for d in deals.values() if d['status']=='completed')}\n"
            f"❌ Отменено: {sum(1 for d in deals.values() if d['status']=='cancelled')}\n\n"
            f"👥 Пользователей: {len(users)}\n"
            f"🚫 Забанено: {len(banned_users)}\n"
            f"🏆 В топе: {len(top_deals)}"
        )
        edit(chat_id, msg_id, t, kb_admin())
        return

    if data == "a_broadcast":
        user_states[user_id] = "a_broadcast"
        edit(chat_id, msg_id, "<b>📢 Введите текст рассылки:</b>")
        return

    if data == "a_ban":
        user_states[user_id] = "a_ban"
        edit(chat_id, msg_id, "<b>🚫 Введите @username или ID для бана:</b>")
        return

    if data == "a_unban":
        user_states[user_id] = "a_unban"
        edit(chat_id, msg_id, "<b>✅ Введите @username или ID для разбана:</b>")
        return

    if data == "a_banner":
        user_states[user_id] = "a_banner"
        edit(chat_id, msg_id,
             f"<b>📝 Введите новый текст баннера:</b>\n\n<b>Текущий:</b>\n{settings['banner_text']}")
        return

    if data == "a_deals":
        if not deals:
            edit(chat_id, msg_id, "<b>📭 Сделок пока нет</b>", kb_admin())
            return
        icons = {"waiting": "⏳", "in_progress": "🔄", "cancelled": "❌", "completed": "✅"}
        t = "<b>📋 ПОСЛЕДНИЕ 10 СДЕЛОК:</b>\n\n"
        for did, d in list(deals.items())[-10:]:
            t += f"{icons.get(d['status'],'❓')} <code>{did}</code>: @{d['creator_name']} → @{d['second_user']} ({d['amount']} {d['currency']})\n"
        if len(deals) > 10:
            t += f"\n<i>...и ещё {len(deals)-10} сделок</i>"
        edit(chat_id, msg_id, t, kb_admin())
        return

    if data == "a_top":
        top_deals = generate_top()
        t = "<b>🔄 ТОП-15 ОБНОВЛЁН:</b>\n\n"
        for i, d in enumerate(top_deals[:15], 1):
            t += f"<b>{i}.</b> {mask(d['user1'])} ↔ {mask(d['user2'])} — {d['amount']} {d['currency']}\n"
        edit(chat_id, msg_id, t, kb_admin())
        return

    if data == "a_close":
        delete(chat_id, msg_id)
        send(chat_id, settings["banner_text"], kb_main())
        return

# ===== MAIN LOOP =====
def main():
    global top_deals

    print(f"🚀 Bot @{BOT_USERNAME} запущен")
    print(f"👑 Admin IDs: {ADMIN_IDS}")

    top_deals = generate_top()
    tg("deleteWebhook", {})

    offset = 0
    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35,
            )
            if r.status_code == 200:
                data = r.json()
                if data.get("ok"):
                    for upd in data["result"]:
                        offset = upd["update_id"] + 1
                        try:
                            if "message" in upd:
                                handle_message(upd["message"])
                            elif "callback_query" in upd:
                                handle_callback(upd["callback_query"])
                        except Exception as e:
                            print(f"[handler error] {e}")
            time.sleep(0.3)
        except KeyboardInterrupt:
            print("❌ Бот остановлен")
            break
        except Exception as e:
            print(f"[loop error] {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
