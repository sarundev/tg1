"""Configuration and message content, all in one place.

Edit MESSAGES below to change the wording; edit .env to change tokens/links.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _env(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


BOT_TOKEN = _env("BOT_TOKEN")

BANNER_URL = _env("BANNER_URL")
BANNER_PATH = BASE_DIR / _env("BANNER_PATH", "assets/poster1.jpg")

REGISTER_URL = _env("REGISTER_URL", "https://t.me/sb24lucky98999")
CHANNEL_URL = _env("CHANNEL_URL", "https://t.me/sb24lucky98999")
SUPPORT_URL = _env("SUPPORT_URL", "https://t.me/sb24lucky98999")

_admin = _env("ADMIN_CHAT_ID")
ADMIN_CHAT_ID = int(_admin) if _admin.lstrip("-").isdigit() else None

BRAND = _env("BRAND", "G168 Sport")

# ── Text shown to users (HTML parse mode) ───────────────────────────────
WELCOME_CAPTION = (
    "<b>{brand}</b> ឧត្តមភាពក្នុងការផ្តល់សេវាជូនអតិថិជន <b>24/7</b>\n"
    "ផ្តល់ជូនសេវាកម្មរហ័ស ប្រកបដោយសុជីវធម៌ និងប្រសិទ្ធភាពខ្ពស់បំផុត។\n"
    "\n"
    "ចុះឈ្មោះឥឡូវនេះ នឹងទទួលបានអារម្មណ៍ដ៏ស្រស់ស្អាតពីពួកយើង!"
)

HELP_TEXT = (
    "<b>ជំនួយ / Help</b>\n"
    "\n"
    "/start — ទទួលបានតំណភ្ជាប់ចុះឈ្មោះ\n"
    "/help — មើលបញ្ជីពាក្យបញ្ជា\n"
    "/support — ទាក់ទងផ្នែកបម្រើអតិថិជន"
)

SUPPORT_TEXT = (
    "ក្រុមការងារបម្រើអតិថិជនរបស់យើងបម្រើសេវា <b>24/7</b>។\n"
    "សូមចុចប៊ូតុងខាងក្រោមដើម្បីជជែកផ្ទាល់។"
)

# ── Inline button labels ────────────────────────────────────────────────
BTN_REGISTER = "📝 ចុះឈ្មោះគណនីថ្មីឥឡូវនេះ"
BTN_CHANNEL = "📢 ឆានែលតេឡេក្រាម"
BTN_SUPPORT = "📞 ទំនាក់ទំនងផ្នែកបម្រើអតិថិជន"

# ── Commands shown in the "/" menu ──────────────────────────────────────
BOT_COMMANDS = [
    ("start", "ចាប់ផ្តើម / Start"),
]
