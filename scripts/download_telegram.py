import os
import base64
import asyncio
import json
from pathlib import Path
from telethon import TelegramClient
import logging

# Enable logging برای دیدن مشکل
logging.basicConfig(level=logging.INFO)

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
        
        # Setup directories - مطمئن شو که دایرکتوری‌ها ایجاد می‌شوند
        session_dir = Path('sessions')
        files_dir = Path('telegram_files')
        session_dir.mkdir(parents=True, exist_ok=True)
        files_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📂 Working directory: {Path.cwd()}")
        print(f"📂 Session dir: {session_dir.absolute()}")
        print(f"📂 Files dir: {files_dir.absolute()}")
        
        # Decode and save session
        try:
            session_bytes = base64.b64decode(SESSION_B64)
            session_file = session_dir / 'telegram_session.session'
            with open(session_file, 'wb') as f:
                f.write(session_bytes)
            print(f"✅ Session ذخیره شد: {session_file.absolute()}")
        except Exception as e:
            print(f"❌ خطا در decode کردن session: {e}")
            exit(1)
        
        # Create Client with timeout
        print("⏳ درحال اتصال به تلگرام...")
        client = TelegramClient(
            str(session_dir / 'telegram_session'), 
            API_ID, 
            API_HASH,
            connection_retries=5,
            retry_delay=1,
            flood_sleep_threshold=120
        )
        
        await client.connect()
        print("✅ متصل شدم")
        
        if not await client.is_user_authorized():
            print("❌ Session معتبر نیست!")
            await client.disconnect()
            exit(1)
        
        print("✅ تایید هویت انجام شد")
        
        # یافتن آخرین فایل
        print(f"⏳ درحال جستجوی آخرین فایل در چنل {CHANNEL_ID}...")
        
        last_file = None
        message_count = 0
        
        async for message in client.iter_messages(CHANNEL_ID, limit=None):
            message_count += 1
            
            if message.document:
                # Extract filename
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
                
                last_file = {
                    'message': message,
                    'filename': filename,
                    'size': message.document.size,
                    'message_id': message.id
                }
                
                # خروج از حلقه (آخرین فایل پیدا شد)
                break
        
        if not last_file:
            print(f"❌ فایلی در چنل پیدا نشد! (بررسی شد: {message_count} پیام)")
            await client.disconnect()
            exit(1)
        
        # دانلود آخرین فایل
        filename = last_file['filename']
        filepath = files_dir / filename
        file_size = last_file['size']
        
        print(f"\n📄 آخرین فایل:")
        print(f"   نام: {filename}")
        print(f"   اندازه: {file_size / (1024*1024):.2f} MB")
        print(f"   پیام ID: {last_file['message_id']}")
        
        if filepath.exists():
            print(f"⏭️  فایل قبلاً دانلود شده است")
            print(f"   مسیر: {filepath.absolute()}")
        else:
            print(f"⬇️  درحال دانلود...")
            await client.download_media(last_file['message'], str(filepath))
            print(f"✅ دانلود کامل شد")
            print(f"   مسیر: {filepath.absolute()}")
        
        # بررسی اینکه فایل واقعاً وجود دارد
        if not filepath.exists():
            print(f"❌ خطا: فایل بعد از دانلود پیدا نشد!")
            await client.disconnect()
            exit(1)
        
        actual_size = filepath.stat().st_size
        print(f"   اندازه واقعی: {actual_size / (1024*1024):.2f} MB")
        
        # ذخیره اطلاعات
        file_info = {
            'filename': filename,
            'size': actual_size,
            'message_id': last_file['message_id'],
            'download_path': str(filepath.absolute())
        }
        
        info_file = files_dir / 'file_info.json'
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(file_info, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ اطلاعات ذخیره شد")
        print(f"   فایل: {info_file.absolute()}")
        
        # ذخیره file_info.json در root هم برای سازگاری
        root_info_file = Path('file_info.json')
        with open(root_info_file, 'w', encoding='utf-8') as f:
            json.dump(file_info, f, ensure_ascii=False, indent=2)
        print(f"   فایل (root): {root_info_file.absolute()}")
        
        await client.disconnect()
        print("✅ اتصال قطع شد")
        
    except asyncio.TimeoutError:
        print("❌ Timeout: اتصال تلگرام قطع شد")
        exit(1)
    except Exception as e:
        print(f"❌ خطای کلی: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
