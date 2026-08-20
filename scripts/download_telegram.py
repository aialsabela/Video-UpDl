import os
import base64
import asyncio
import json
from telethon import TelegramClient

async def main():
    # Secrets
    API_ID = int(os.getenv('TELEGRAM_API_ID'))
    API_HASH = os.getenv('TELEGRAM_API_HASH')
    CHANNEL_ID = int(os.getenv('TELEGRAM_CHANNEL_ID'))
    SESSION_B64 = os.getenv('TELEGRAM_SESSION')
    
    # Decode Session
    session_bytes = base64.b64decode(SESSION_B64)
    with open('telegram_session.session', 'wb') as f:
        f.write(session_bytes)
    
    # Create Client
    client = TelegramClient('telegram_session', API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("❌ Session معتبر نیست!")
        exit(1)
    
    print("✅ متصل شدم")
    
    # آخرین فایل
    os.makedirs('telegram_files', exist_ok=True)
    
    async for message in client.iter_messages(CHANNEL_ID, limit=100):
        if message.document:
            filename = message.document.filename or f"file_{message.id}"
            filepath = f"telegram_files/{filename}"
            
            print(f"⬇️  درحال دانلود: {filename}")
            await client.download_media(message, filepath)
            
            # ذخیره اطلاعات
            with open('file_info.json', 'w') as f:
                json.dump({
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'message_id': message.id
                }, f)
            
            print(f"✅ دانلود کامل: {filename}")
            break
    
    await client.disconnect()

asyncio.run(main())
