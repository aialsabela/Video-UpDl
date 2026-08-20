import os
import asyncio
import json
from telethon import TelegramClient

async def download_latest_file():
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    channel_id = int(os.getenv('TELEGRAM_CHANNEL_ID'))
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    client = TelegramClient('bot_session', api_id, api_hash)
    
    try:
        await client.start(bot_token=bot_token)
        print("✅ اتصال برقرار شد")
        
        async with client:
            latest_file = None
            latest_message = None
            
            # آخرین فایل را پیدا کنید
            async for message in client.iter_messages(channel_id, limit=100):
                if message.document:
                    latest_file = message.document
                    latest_message = message
                    break
            
            if not latest_file:
                print("❌ هیچ فایلی پیدا نشد")
                return
            
            # نام فایل
            filename = latest_file.attributes[0].file_name
            print(f"📥 دانلود: {filename}")
            
            # دایرکتوری ایجاد کنید
            os.makedirs('telegram_files', exist_ok=True)
            filepath = f'telegram_files/{filename}'
            
            # دانلود فایل
            await client.download_media(latest_message, file=filepath)
            
            # اطلاعات
            file_size = os.path.getsize(filepath)
            print(f"✅ دانلود شد: {file_size / 1024 / 1024:.2f} MB")
            
            # ذخیره متادیتا
            metadata = {
                'filename': filename,
                'size': file_size,
                'message_id': latest_message.id
            }
            
            with open('file_info.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"📄 متادیتا ذخیره شد")
    
    except Exception as e:
        print(f"❌ خطا: {e}")
        raise
    
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(download_latest_file())
