import os
import shutil
from pathlib import Path
import json

CHUNK_SIZE = 100 * 1024 * 1024  # ۱۰۰ مگابایت
OUTPUT_DIR = 'uploaded_files'

def split_file(filepath, chunk_size=CHUNK_SIZE):
    """فایل بزرگ را به قسمت‌های کوچک تقسیم می‌کند"""
    
    filename = Path(filepath).name
    file_size = os.path.getsize(filepath)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # اگر کوچک‌تر از ۱۰۰ مگ است، تقسیم نکن
    if file_size <= chunk_size:
        print(f"✅ {filename} کوچک‌تر از ۱۰۰ مگ است")
        shutil.copy(filepath, f'{OUTPUT_DIR}/{filename}')
        return [filename]
    
    print(f"📊 {filename} بزرگ است ({file_size / (1024**2):.2f} MB)")
    print(f"🔪 در حال تقسیم به قسمت‌های ۱۰۰ مگابایتی...")
    
    parts = []
    with open(filepath, 'rb') as f:
        part_num = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            part_filename = f'{filename}.part{part_num}'
            part_filepath = f'{OUTPUT_DIR}/{part_filename}'
            
            with open(part_filepath, 'wb') as part_file:
                part_file.write(chunk)
            
            part_size = len(chunk) / (1024**2)
            print(f"  ✓ قسمت {part_num}: {part_size:.2f} MB")
            parts.append(part_filename)
            part_num += 1
    
    return parts

def process_files():
    """تمام فایل‌های دانلود شده را پردازش می‌کند"""
    
    if not os.path.exists('telegram_files'):
        print("❌ پوشه telegram_files پیدا نشد")
        return []
    
    all_parts = []
    for filename in os.listdir('telegram_files'):
        filepath = f'telegram_files/{filename}'
        if os.path.isfile(filepath):
            parts = split_file(filepath)
            all_parts.extend(parts)
    
    # ذخیره لیست فایل‌ها برای Release
    with open('release_files.json', 'w') as f:
        json.dump({'files': all_parts}, f)
    
    print("✅ پردازش تمام شد")
    return all_parts

if __name__ == '__main__':
    process_files()
