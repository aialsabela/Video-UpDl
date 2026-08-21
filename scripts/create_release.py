import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

def create_release():
    release_file = Path('release_files.json')
    
    if not release_file.exists():
        print("❌ release_files.json پیدا نشد")
        print(f"   Working directory: {Path.cwd()}")
        print(f"   Contents: {list(Path.cwd().glob('*'))}")
        return False
    
    print(f"📋 release_files.json پیدا شد: {release_file.absolute()}")
    
    with open(release_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    files = data.get('parts', [])
    
    if not files:
        print("❌ فایلی برای آپلود پیدا نشد")
        return False
    
    # بررسی وجود فایل‌ها
    uploaded_dir = Path('uploaded_files')
    for file in files:
        file_path = uploaded_dir / file
        if not file_path.exists():
            print(f"❌ فایل پیدا نشد: {file}")
            print(f"   جستجو شد در: {file_path.absolute()}")
            return False
    
    # ایجاد tag منحصر‌به‌فرد
    tag = f"release-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"\n📤 درحال آپلود Release: {tag}")
    print(f"📊 تعداد فایل‌ها: {len(files)}\n")
    
    try:
        # استفاده از subprocess برای امنیت بیشتر
        file_args = [str(uploaded_dir / f) for f in files]
        cmd = ['gh', 'release', 'create', tag, '--generate-notes'] + file_args
        
        print(f"⏳ درحال آپلود...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print(f"✅ Release {tag} آپلود شد!")
        print(f"📊 {len(files)} فایل آپلود شد")
        
        # نمایش خروجی
        if result.stdout:
            print(f"\n📝 خروجی:")
            print(result.stdout)
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در آپلود: {e.stderr}")
        print(f"stdout: {e.stdout}")
        return False
    except FileNotFoundError:
        print("❌ gh CLI نصب نشده است")
        print("   نصب کنید: https://cli.github.com")
        return False
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_release()
    exit(0 if success else 1)
