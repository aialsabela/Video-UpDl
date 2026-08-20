import os
import asyncio
from telethon import TelegramClient
import json

async def download_latest_file():
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    channel_id = int(os.getenv('TELEGRAM_CHANNEL_ID'))
    
    async with TelegramClient('session', api_id, api_hash) as client:
        print("📡 اتصال به تلگرام...")
        
        # دریافت آخرین ۵ پیام
        messages = []
        async for message in client.iter_messages(channel_id, limit=5):
            if message.document:
                messages.append(message)
        
        if not messages:
            print("❌ فایلی یافت نشد")
            return
        
        # آخرین فایل
        latest_message = messages[0]
        filename = latest_message.document.attributes[0].file_name
        file_size = latest_message.document.size
        
        print(f"📥 دانلود: {filename}")
        print(f"📊 حجم: {file_size / (1024**2):.2f} MB")
        
        # پوشه آپلود
        os.makedirs('telegram_files', exist_ok=True)
        filepath = f'telegram_files/{filename}'
        
        # دانلود
        await client.download_media(latest_message, file=filepath)
        print(f"✅ دانلود کامل")
        
        # ذخیره اطلاعات فایل
        with open('file_info.json', 'w') as f:
            json.dump({
                'filename': filename,
                'size': file_size,
                'message_id': latest_message.id
            }, f)

asyncio.run(download_latest_file())
