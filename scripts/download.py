"""
دانلود فایل از یک پیام تلگرام با استفاده از Telethon.
ورودی MESSAGE_LINK می‌تونه یکی از این دو حالت باشه:
  - فقط آیدی عددی پیام (مثل 123) → از TELEGRAM_CHANNEL_ID به‌عنوان چت استفاده می‌شود
  - لینک کامل پیام (مثل https://t.me/channel_username/123
    یا https://t.me/c/1234567890/123) → چت از خود لینک استخراج می‌شود
"""

import os
import re
import sys
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
MESSAGE_LINK = os.environ["MESSAGE_LINK"].strip()

DOWNLOAD_DIR = "downloads"


def resolve_chat_and_msg(value: str):
    # فقط عدد یعنی آیدی پیام؛ چت از TELEGRAM_CHANNEL_ID گرفته می‌شود
    if value.isdigit():
        if not CHANNEL_ID:
            raise ValueError("TELEGRAM_CHANNEL_ID تنظیم نشده و ورودی فقط آیدی پیام است.")
        chat = int(CHANNEL_ID) if re.fullmatch(r"-?\d+", CHANNEL_ID) else CHANNEL_ID
        return chat, int(value)

    # فرمت خصوصی: https://t.me/c/1234567890/123
    m = re.search(r"t\.me/c/(\d+)/(\d+)", value)
    if m:
        chat_id = int("-100" + m.group(1))
        msg_id = int(m.group(2))
        return chat_id, msg_id

    # فرمت عمومی: https://t.me/username/123
    m = re.search(r"t\.me/([^/]+)/(\d+)", value)
    if m:
        username = m.group(1)
        msg_id = int(m.group(2))
        return username, msg_id

    raise ValueError(f"مقدار MESSAGE_LINK قابل تشخیص نیست: {value}")


async def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    chat, msg_id = resolve_chat_and_msg(MESSAGE_LINK)

    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        message = await client.get_messages(chat, ids=msg_id)
        if message is None or not message.file:
            print("::error::پیامی با فایل ضمیمه در این آدرس پیدا نشد.")
            sys.exit(1)

        print(f"در حال دانلود: {message.file.name or 'بدون‌نام'} "
              f"({message.file.size / (1024*1024):.2f} MB)")

        path = await message.download_media(file=DOWNLOAD_DIR + "/")
        print(f"دانلود کامل شد: {path}")

        # مسیر فایل رو برای مرحله بعدی workflow خروجی می‌دیم
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write(f"file_path={path}\n")


if __name__ == "__main__":
    asyncio.run(main())
