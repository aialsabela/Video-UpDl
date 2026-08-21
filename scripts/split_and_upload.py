import os
import json
from pathlib import Path

CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB

def split_file():
    files_dir = Path('telegram_files')
    
    # بررسی وجود دایرکتوری
    if not files_dir.exists():
        print("❌ دایرکتوری telegram_files پیدا نشد")
        return
    
    # یافتن file_info.json
    info_file = files_dir / 'file_info.json'
    if not info_file.exists():
        print("❌ file_info.json پیدا نشد")
        return
    
    with open(info_file, 'r', encoding='utf-8') as f:
        file_info = json.load(f)
    
    filename = file_info['filename']
    file_size = file_info['size']
    filepath = files_dir / filename
    
    if not filepath.exists():
        print(f"❌ فایل پیدا نشد: {filepath}")
        return
    
    uploaded_dir = Path('uploaded_files')
    uploaded_dir.mkdir(exist_ok=True)
    
    parts_info = []
    
    print(f"📄 فایل: {filename}")
    print(f"📊 اندازه: {file_size / (1024**2):.2f} MB")
    
    if file_size > CHUNK_SIZE:
        print(f"📦 فایل بزرگ است - درحال تقسیم...")
        print(f"✂️  قسمت‌های 100MB...")
        
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
                
                parts_info.append(part_name)
                print(f"   ✅ {part_name} ({len(chunk) / (1024**2):.2f} MB)")
                part_num += 1
        
        print(f"✅ {len(parts_info)} قسمت ایجاد شد\n")
    else:
        print(f"📄 فایل کوچک است - بدون تقسیم")
        new_path = uploaded_dir / filename
        
        if new_path.exists():
            print(f"   ⏭️  فایل قبلاً موجود است")
        else:
            os.rename(filepath, new_path)
            print(f"   ✅ کپی شد")
        
        parts_info.append(filename)
        print()
    
    # ذخیره اطلاعات Release
    release_file = Path('release_files.json')
    with open(release_file, 'w', encoding='utf-8') as f:
        json.dump({
            'parts': parts_info,
            'total_parts': len(parts_info),
            'original_filename': filename,
            'original_size': file_size
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(parts_info)} فایل آماده برای Release")
    print(f"📋 release_files.json ایجاد شد")

if __name__ == "__main__":
    split_file()
