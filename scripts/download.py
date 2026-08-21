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
SESSION = os.environ["TELEGRAM_SESSION"].strip()
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
MESSAGE_LINK = os.environ["MESSAGE_LINK"].strip()

DOWNLOAD_DIR = "downloads"

if not SESSION or len(SESSION) < 50:
    print("::error::مقدار Secret به نام TELEGRAM_SESSION خالی یا نامعتبر است. "
          "دوباره scripts/generate_session.py را اجرا کنید و کل رشته خروجی را "
          "بدون فاصله یا کوتیشن اضافه در Secret جایگذاری کنید.")
    sys.exit(1)


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

        total_mb = message.file.size / (1024 * 1024)
        print(f"در حال دانلود: {message.file.name or 'بدون‌نام'} ({total_mb:.2f} MB)")

        last_percent = [-10]

        def progress(current, total):
            percent = int(current * 100 / total)
            if percent >= last_percent[0] + 10:
                last_percent[0] = percent
                print(f"پیشرفت دانلود: {percent}% "
                      f"({current / (1024*1024):.1f} / {total_mb:.1f} MB)")

        path = await message.download_media(
            file=DOWNLOAD_DIR + "/",
            progress_callback=progress,
        )

        if not path:
            print("::error::download_media مسیری برنگرداند؛ دانلود انجام نشد.")
            sys.exit(1)

        abs_path = os.path.abspath(path)
        size_mb = os.path.getsize(abs_path) / (1024 * 1024)
        print(f"دانلود کامل شد: {abs_path} ({size_mb:.2f} MB)")

        # مسیر فایل رو برای مرحله بعدی workflow خروجی می‌دیم
        github_output = os.environ.get("GITHUB_OUTPUT")
        if not github_output:
            print("::error::متغیر GITHUB_OUTPUT موجود نیست؛ خروجی file_path ست نمی‌شود.")
            sys.exit(1)

        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"file_path={abs_path}\n")
        print(f"خروجی file_path با موفقیت روی GITHUB_OUTPUT نوشته شد: {abs_path}")


if __name__ == "__main__":
    asyncio.run(main())
