import asyncio
import base64
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

async def generate_session():
    print("="*60)
    print("🔐 تولید Telegram Session")
    print("="*60)
    
    print("\n📝 اطلاعات رو وارد کن:\n")
    API_ID = int(input("API_ID: "))
    API_HASH = input("API_HASH: ")
    PHONE = input("شماره تلفن (+98...): ")
    
    print("\n⏳ درحال اتصال...")
    
    client = TelegramClient('telegram_session', API_ID, API_HASH)
    await client.connect()
    
    try:
        print("📱 کد OTP برایت فرستاده شد")
        await client.send_code_request(PHONE)
        code = input("کد OTP رو وارد کن: ")
        await client.sign_in(PHONE, code)
    except SessionPasswordNeededError:
        print("🔒 رمز ۲ مرحله‌ای فعال است")
        password = input("رمز رو وارد کن: ")
        await client.sign_in(password=password)
    
    print("\n✅ Login موفق!")
    
    with open('telegram_session.session', 'rb') as f:
        session_bytes = f.read()
    
    session_b64 = base64.b64encode(session_bytes).decode()
    
    print("\n" + "="*60)
    print("📋 TELEGRAM_SESSION:")
    print("="*60)
    print(session_b64)
    print("="*60)
    
    await client.disconnect()

asyncio.run(generate_session())
