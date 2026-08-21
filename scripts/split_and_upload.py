import os
import json
from pathlib import Path
import subprocess

CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB

def split_file():
    files_dir = Path('telegram_files')
    
    # بررسی وجود دایرکتوری
    if not files_dir.exists():
        print("❌ دایرکتوری telegram_files پیدا نشد")
        return
    
    # یافتن فایل‌های دانلود‌شده
    info_file = files_dir / 'downloaded_files.json'
    if not info_file.exists():
        print("❌ downloaded_files.json پیدا نشد")
        return
    
    with open(info_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data.get('files'):
        print("❌ فایلی برای تقسیم پیدا نشد")
        return
    
    uploaded_dir = Path('uploaded_files')
    uploaded_dir.mkdir(exist_ok=True)
    
    parts_info = []
    
    # پردازش تمام فایل‌ها
    for file_info in data['files']:
        filename = file_info['filename']
        filepath = files_dir / filename
        file_size = file_info['size']
        
        if not filepath.exists():
            print(f"⚠️  پرتاب شد: {filename} (موجود نیست)")
            continue
        
        if file_size > CHUNK_SIZE:
            print(f"📦 فایل بزرگ: {filename} ({file_size / (1024**2):.2f} MB)")
            print(f"✂️  درحال تقسیم...")
            
            parts = []
            with open(filepath, 'rb') as f:
                part_num = 1
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    part_name = f"{filename}.part{part_num:03d}"
                    part_path = uploaded_dir / part_name
                    
                    with open(part_path, 'wb') as pf:
                        pf.write(chunk)
                    
                    parts.append(part_name)
                    print(f"✅ {part_name} ({len(chunk) / (1024**2):.2f} MB)")
                    part_num += 1
            
            parts_info.extend(parts)
            print(f"✅ {len(parts)} قسمت ایجاد شد برای {filename}\n")
        else:
            print(f"📄 فایل کوچک: {filename} ({file_size / (1024**2):.2f} MB)")
            new_path = uploaded_dir / filename
            
            if new_path.exists():
                print(f"   ⏭️  موجود است، پرتاب شد")
                continue
            
            os.rename(filepath, new_path)
            parts_info.append(filename)
            print(f"✅ کپی شد\n")
    
    # ذخیره خلاصه
    if parts_info:
        release_file = Path('release_files.json')
        with open(release_file, 'w', encoding='utf-8') as f:
            json.dump({
                'parts': parts_info,
                'total_parts': len(parts_info),
                'message': 'Ready for release'
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(parts_info)} فایل آماده برای Release")
    else:
        print("❌ فایلی برای آپلود پیدا نشد")

if __name__ == "__main__":
    split_file()
