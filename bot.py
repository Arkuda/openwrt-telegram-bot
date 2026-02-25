import logging
import os
import shlex
import subprocess
from typing import Iterable

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("openwrt_bot")

COMMAND_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["/start", "/clients", "/openvpn"],
        ["/interfaces", "/rua_status", "/rua_update"],
        ["/rua_add example.com"],
    ],
    resize_keyboard=True,
)


async def reply_with_keyboard(update: Update, text: str) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(text, reply_markup=COMMAND_KEYBOARD)


def parse_allowed_chat_ids(raw_value: str | None) -> set[int]:
    if not raw_value:
        return set()

    parsed: set[int] = set()
    for item in raw_value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            parsed.add(int(item))
        except ValueError:
            logger.warning("Skipping invalid chat id value: %s", item)
    return parsed


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ALLOWED_CHAT_IDS = parse_allowed_chat_ids(os.getenv("ALLOWED_CHAT_IDS"))
RUANTIBLOCK_STATUS_CMD = os.getenv("RUANTIBLOCK_STATUS_CMD", "ruantiblock status")
RUANTIBLOCK_ADD_CMD = os.getenv("RUANTIBLOCK_ADD_CMD", "ruantiblock add list1 {domain}")
RUANTIBLOCK_UPDATE_CMD = os.getenv("RUANTIBLOCK_UPDATE_CMD", "ruantiblock update")


def run_command(command: str) -> str:
    try:
        completed = subprocess.run(
            command,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=20,
        )
        output = completed.stdout.strip()
        if not output:
            output = "(пустой вывод)"
        return output
    except subprocess.TimeoutExpired:
        return "Команда завершилась по таймауту"


def is_authorized(chat_id: int) -> bool:
    # Если ALLOWED_CHAT_IDS не задан или пустой — по умолчанию запрещаем всем.
    if not ALLOWED_CHAT_IDS:
        return False
    return chat_id in ALLOWED_CHAT_IDS


async def ensure_authorized(update: Update) -> bool:
    chat = update.effective_chat
    if chat is None:
        return False

    chat_id = chat.id
    if is_authorized(chat_id):
        return True

    message = (
        f"Несанкционированный доступ из чата {chat_id}, "
        "инцидент будет залогирован"
    )
    await reply_with_keyboard(update, message)

    logger.warning("Unauthorized access from chat_id=%s", chat_id)
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_authorized(update):
        return
    await reply_with_keyboard(
        update,
        "Бот запущен. Команды: /clients, /openvpn, /interfaces, /rua_status, /rua_add <domain>, /rua_update",
    )


async def clients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_authorized(update):
        return
    output = run_command("cat /tmp/dhcp.leases")
    await reply_with_keyboard(update, f"Клиенты:\n{output}")


async def openvpn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_authorized(update):
        return
    output = run_command("ifstatus openvpn 2>/dev/null || /etc/init.d/openvpn status")
    await reply_with_keyboard(update, f"OpenVPN:\n{output}")


async def interfaces(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_authorized(update):
        return
    commands: Iterable[tuple[str, str]] = (
        ("LAN", "ifstatus lan"),
        ("WAN", "ifstatus wan"),
        ("VPN", "ifstatus vpn"),
    )
    parts = []
    for title, cmd in commands:
        parts.append(f"[{title}]\n{run_command(cmd)}")
    await reply_with_keyboard(update, "\n\n".join(parts))


async def rua_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_authorized(update):
        return
    output = run_command(RUANTIBLOCK_STATUS_CMD)
    await reply_with_keyboard(update, f"ruantiblock:\n{output}")


async def rua_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_authorized(update):
        return
    if not context.args:
        await reply_with_keyboard(update, "Использование: /rua_add <domain>")
        return

    domain = context.args[0].strip()
    safe_domain = shlex.quote(domain)
    output = run_command(RUANTIBLOCK_ADD_CMD.format(domain=safe_domain))
    await reply_with_keyboard(update, f"Добавление в list1:\n{output}")


async def rua_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_authorized(update):
        return
    output = run_command(RUANTIBLOCK_UPDATE_CMD)
    await reply_with_keyboard(update, f"Обновление ruantiblock:\n{output}")


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_authorized(update):
        return
    await reply_with_keyboard(update, "Неизвестная команда. Используй /start")


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN не задан")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clients", clients))
    app.add_handler(CommandHandler("openvpn", openvpn))
    app.add_handler(CommandHandler("interfaces", interfaces))
    app.add_handler(CommandHandler("rua_status", rua_status))
    app.add_handler(CommandHandler("rua_add", rua_add))
    app.add_handler(CommandHandler("rua_update", rua_update))
    app.add_handler(MessageHandler(filters.ALL, unknown_message))

    logger.info("Starting bot")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
