# openwrt-telegram-bot

Простой Telegram-бот для OpenWrt.

## Возможности
- Доступ к shell-командам роутера через Telegram-команды.
- ReplyKeyboardMarkup с кнопками команд отображается в каждом ответе бота.
- Вывод клиентов (`/clients`), OpenVPN (`/openvpn`), интерфейсов (`/interfaces`).
- Статус `ruantiblock_openwrt` (`/rua_status`).
- Добавление домена в `list1` (`/rua_add <domain>`).
- Обновление списков `ruantiblock_openwrt` (`/rua_update`).

## Защита по chat_id
- Используется переменная `ALLOWED_CHAT_IDS` (список id через запятую).
- Если `ALLOWED_CHAT_IDS` не указана или пустая, бот **по умолчанию запрещает доступ всем чатам**.
- В таком случае (или если chat_id не входит в список) бот отвечает:
  `Несанкционированный доступ из чата <chat_id>, инцидент будет залогирован`.

## Настройка
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Переменные окружения
- `TELEGRAM_TOKEN` — токен бота (обязательно).
- `ALLOWED_CHAT_IDS` — например: `12345,67890`.
- `RUANTIBLOCK_STATUS_CMD` — команда для статуса (по умолчанию `ruantiblock status`).
- `RUANTIBLOCK_ADD_CMD` — команда добавления в list1 (по умолчанию `ruantiblock add list1 {domain}`).
- `RUANTIBLOCK_UPDATE_CMD` — команда обновления (по умолчанию `ruantiblock update`).

## Запуск
```bash
export TELEGRAM_TOKEN='...'
export ALLOWED_CHAT_IDS='123456789'
python3 bot.py
```
