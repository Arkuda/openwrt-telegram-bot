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

## Ручной запуск
```bash
export TELEGRAM_TOKEN='...'
export ALLOWED_CHAT_IDS='123456789'
python3 bot.py
```

## Запуск как сервис OpenWrt (procd)
В репозитории добавлены файлы:
- `openwrt/openwrt-telegram-bot.init` — init-скрипт `/etc/init.d/openwrt-telegram-bot`
- `openwrt/openwrt-telegram-bot.config` — пример `/etc/config/openwrt-telegram-bot`

Установка на роутере:
```sh
# 1) Скопировать проект на роутер, например:
mkdir -p /opt/openwrt-telegram-bot
# ...скопировать bot.py, requirements.txt и установить зависимости

# 2) Установить init-скрипт
cp /opt/openwrt-telegram-bot/openwrt/openwrt-telegram-bot.init /etc/init.d/openwrt-telegram-bot
chmod +x /etc/init.d/openwrt-telegram-bot

# 3) Установить конфиг
cp /opt/openwrt-telegram-bot/openwrt/openwrt-telegram-bot.config /etc/config/openwrt-telegram-bot

# 4) Заполнить токен/доступы
uci set openwrt-telegram-bot.bot.enabled='1'
uci set openwrt-telegram-bot.bot.telegram_token='YOUR_BOT_TOKEN'
uci set openwrt-telegram-bot.bot.allowed_chat_ids='123456789,987654321'
uci set openwrt-telegram-bot.bot.bot_path='/opt/openwrt-telegram-bot/bot.py'
uci commit openwrt-telegram-bot

# 5) Включить автозапуск и старт
/etc/init.d/openwrt-telegram-bot enable
/etc/init.d/openwrt-telegram-bot start
```

Проверка:
```sh
/etc/init.d/openwrt-telegram-bot status
logread -e openwrt-telegram-bot
```
