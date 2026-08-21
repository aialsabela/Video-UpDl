import os
import base64
import asyncio
import json
from pathlib import Path
from telethon import TelegramClient

async def main():
    try:
        # Secrets
        API_ID = int(os.getenv('TELEGRAM_API_ID'))
        API_HASH = os.getenv('TELEGRAM_API_HASH')
        CHANNEL_ID = int(os.getenv('TELEGRAM_CHANNEL_ID'))
        SESSION_B64 = os.getenv('TELEGRAM_SESSION')
        
        # Validate environment variables
        if not all([API_ID, API_HASH, CHANNEL_ID, SESSION_B64]):
            print("❌ متغیرهای محیطی ناقص هستند!")
            exit(1)
        
        # Setup directories
        session_dir = Path('sessions')
        files_dir = Path('telegram_files')
        session_dir.mkdir(exist_ok=True)
        files_dir.mkdir(exist_ok=True)
        
        # Decode and save session
        try:
            session_bytes = base64.b64decode(SESSION_B64)
            session_file = session_dir / 'telegram_session.session'
            with open(session_file, 'wb') as f:
                f.write(session_bytes)
        except Exception as e:
            print(f"❌ خطا در decode کردن session: {e}")
            exit(1)
        
        # Create Client
        client = TelegramClient(str(session_dir / 'telegram_session'), API_ID, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ Session معتبر نیست!")
            await client.disconnect()
            exit(1)
        
        print("✅ متصل شدم")
        
        # Downloaded files tracker
        downloaded_files = []
        message_count = 0
        
        # Get files from channel
        async for message in client.iter_messages(CHANNEL_ID, limit=None):
            message_count += 1
            
            if message.document:
                # Extract filename safely
                filename = None
                
                if hasattr(message.document, 'attributes') and message.document.attributes:
                    for attr in message.document.attributes:
                        if hasattr(attr, 'file_name'):
                            filename = attr.file_name
                            break
                
                if not filename:
                    filename = f"file_{message.id}"
                
                # Sanitize filename
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-'))
                filepath = files_dir / filename
                
                # Skip if already downloaded
                if filepath.exists():
                    print(f"⏭️  موجود است: {filename}")
                    continue
                
                try:
                    print(f"⬇️  درحال دانلود: {filename}")
                    await client.download_media(message, str(filepath))
                    
                    # Get file size
                    file_size = filepath.stat().st_size
                    
                    # Store metadata
                    file_info = {
                        'filename': filename,
                        'size': file_size,
                        'message_id': message.id
                    }
                    
                    downloaded_files.append(file_info)
                    
                    # Save individual file info
                    info_file = files_dir / f"{filename}.json"
                    with open(info_file, 'w', encoding='utf-8') as f:
                        json.dump(file_info, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ دانلود کامل: {filename} ({file_size / (1024*1024):.2f} MB)")
                    
                except Exception as e:
                    print(f"❌ خطا در دانلود {filename}: {e}")
                    continue
        
        # Save all downloaded files info
        if downloaded_files:
            summary_file = files_dir / 'downloaded_files.json'
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_messages_checked': message_count,
                    'total_files_downloaded': len(downloaded_files),
                    'files': downloaded_files
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n📊 خلاصه:")
            print(f"   کل پیام‌ها: {message_count}")
            print(f"   فایل‌های دانلود‌شده: {len(downloaded_files)}")
        else:
            print("⚠️  فایل دانلود‌شده‌ای یافت نشد!")
        
        await client.disconnect()
        print("✅ قطع شد")
        
    except Exception as e:
        print(f"❌ خطای کلی: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
