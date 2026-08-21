import os
import json
from pathlib import Path
from datetime import datetime
import subprocess

def create_release():
    release_file = Path('release_files.json')
    
    if not release_file.exists():
        print("❌ release_files.json پیدا نشد")
        return False
    
    with open(release_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    files = data.get('parts', [])
    
    if not files:
        print("❌ فایلی برای آپلود پیدا نشد")
        return False
    
    # بررسی وجود فایل‌ها
    uploaded_dir = Path('uploaded_files')
    for file in files:
        if not (uploaded_dir / file).exists():
            print(f"❌ فایل پیدا نشد: {file}")
            return False
    
    # ایجاد tag منحصر‌به‌فرد
    tag = f"release-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"📤 درحال آپلود Release: {tag}")
    
    try:
        # استفاده از subprocess برای امنیت بیشتر
        file_args = [str(uploaded_dir / f) for f in files]
        cmd = ['gh', 'release', 'create', tag, '--generate-notes'] + file_args
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print(f"✅ Release {tag} آپلود شد!")
        print(f"📊 {len(files)} فایل آپلود شد")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در آپلود: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ gh CLI نصب نشده است")
        print("   نصب کنید: https://cli.github.com")
        return False

if __name__ == "__main__":
    success = create_release()
    exit(0 if success else 1)
