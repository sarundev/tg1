"""JJ7SPORT-style promo bot.

/start replies with a banner image, a caption and three link buttons,
and pins a Mini-App button in the bottom-left corner of the chat.

Run with:  python bot.py
"""
from __future__ import annotations

import logging
import sys

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonCommands,
    MenuButtonWebApp,
    Update,
    WebAppInfo,
)
from telegram.constants import ChatAction, ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("promo-bot")

# Telegram returns a file_id the first time we upload the banner; reusing it
# afterwards makes every later /start a metadata-only call instead of a
# full image upload.
_banner_file_id: str | None = None


def main_keyboard() -> InlineKeyboardMarkup:
    """The three stacked link buttons under the banner."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(config.BTN_REGISTER, url=config.REGISTER_URL)],
            [InlineKeyboardButton(config.BTN_CHANNEL, url=config.CHANNEL_URL)],
            [InlineKeyboardButton(config.BTN_SUPPORT, url=config.SUPPORT_URL)],
        ]
    )


async def send_promo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the banner + caption + buttons, falling back to text-only."""
    global _banner_file_id

    chat = update.effective_chat
    caption = config.WELCOME_CAPTION.format(brand=config.BRAND)
    keyboard = main_keyboard()

    # Priority: cached file_id -> remote URL -> local file on disk.
    photo = _banner_file_id or config.BANNER_URL or None
    handle = None
    if photo is None:
        if config.BANNER_PATH.is_file():
            handle = config.BANNER_PATH.open("rb")
            photo = handle
        else:
            log.warning(
                "No banner: BANNER_URL is empty and %s does not exist.",
                config.BANNER_PATH,
            )

    try:
        if photo:
            await chat.send_action(ChatAction.UPLOAD_PHOTO)
            message = await chat.send_photo(
                photo=photo,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
            if message.photo:
                # Cache the largest rendition for subsequent sends.
                _banner_file_id = message.photo[-1].file_id
        else:
            await chat.send_message(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
    except TelegramError as exc:
        log.warning("Photo send failed (%s); falling back to text.", exc)
        _banner_file_id = None
        await chat.send_message(
            caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    finally:
        if handle is not None:
            handle.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    log.info("/start from %s (%s)", user.id, user.full_name)
    await send_promo(update, context)

    if config.ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                config.ADMIN_CHAT_ID,
                f"👤 New /start: {user.mention_html()} (<code>{user.id}</code>)",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError as exc:
            log.warning("Could not notify admin chat: %s", exc)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html(config.HELP_TEXT)


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html(
        config.SUPPORT_TEXT,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(config.BTN_SUPPORT, url=config.SUPPORT_URL)]]
        ),
    )


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Anything the user types just re-shows the promo."""
    await send_promo(update, context)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Handler error", exc_info=context.error)


async def post_init(application: Application) -> None:
    """Register the '/' command list and the bottom-left menu button."""
    bot = application.bot

    await bot.set_my_commands(config.BOT_COMMANDS)

    if config.MENU_BUTTON_URL.startswith("https://"):
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text=config.MENU_BUTTON_TEXT,
                web_app=WebAppInfo(url=config.MENU_BUTTON_URL),
            )
        )
        log.info("Menu button set to Mini App: %s", config.MENU_BUTTON_URL)
    else:
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
        log.info("MENU_BUTTON_URL not an https URL — using the commands menu.")

    me = await bot.get_me()
    log.info("Running as @%s (id %s)", me.username, me.id)


def main() -> None:
    if not config.BOT_TOKEN:
        sys.exit("BOT_TOKEN is missing. Copy .env.example to .env and fill it in.")

    application = (
        Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    application.add_error_handler(on_error)

    log.info("Polling for updates… (Ctrl-C to stop)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
