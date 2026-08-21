import os
import json
from pathlib import Path

CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB

def split_file():
    # بررسی file_info.json در مسیرهای مختلف
    info_file = None
    
    if Path('file_info.json').exists():
        info_file = Path('file_info.json')
    elif Path('telegram_files/file_info.json').exists():
        info_file = Path('telegram_files/file_info.json')
    else:
        print("❌ file_info.json پیدا نشد")
        print(f"   Working directory: {Path.cwd()}")
        print(f"   Contents: {list(Path.cwd().glob('*'))}")
        return
    
    print(f"📋 file_info.json پیدا شد: {info_file.absolute()}")
    
    with open(info_file, 'r', encoding='utf-8') as f:
        file_info = json.load(f)
    
    filename = file_info['filename']
    file_size = file_info['size']
    
    # جستجوی فایل در مسیرهای مختلف
    filepath = None
    if Path(f"telegram_files/{filename}").exists():
        filepath = Path(f"telegram_files/{filename}")
    elif Path(filename).exists():
        filepath = Path(filename)
    else:
        print(f"❌ فایل پیدا نشد: {filename}")
        print(f"   جستجو شد در:")
        print(f"   - telegram_files/{filename}")
        print(f"   - {filename}")
        print(f"   Working directory: {Path.cwd()}")
        print(f"   Contents: {list(Path.cwd().glob('*'))}")
        return
    
    print(f"✅ فایل پیدا شد: {filepath.absolute()}")
    
    uploaded_dir = Path('uploaded_files')
    uploaded_dir.mkdir(parents=True, exist_ok=True)
    
    parts_info = []
    
    print(f"\n📄 فایل: {filename}")
    print(f"📊 اندازه: {file_size / (1024**2):.2f} MB")
    
    if file_size > CHUNK_SIZE:
        print(f"📦 فایل بزرگ است - درحال تقسیم...")
        print(f"✂️  قسمت‌های 100MB...\n")
        
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
        
        print(f"\n✅ {len(parts_info)} قسمت ایجاد شد\n")
    else:
        print(f"📄 فایل کوچک است - بدون تقسیم\n")
        new_path = uploaded_dir / filename
        
        if new_path.exists():
            print(f"   ⏭️  فایل قبلاً موجود است")
        else:
            # Copy فایل به جای move برای جلوگیری از مشکلات
            import shutil
            shutil.copy2(filepath, new_path)
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
    print(f"📋 release_files.json ایجاد شد: {release_file.absolute()}")

if __name__ == "__main__":
    split_file()
