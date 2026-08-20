import os
import subprocess
import json
from datetime import datetime

def create_release():
    """Release جدید ایجاد می‌کند و فایل‌ها را آپلود می‌کند"""
    
    if not os.path.exists('release_files.json'):
        print("❌ فایلی برای آپلود وجود ندارد")
        return
    
    with open('release_files.json', 'r') as f:
        data = json.load(f)
        files = data['files']
    
    # خواندن اطلاعات فایل اصلی
    with open('file_info.json', 'r') as f:
        file_info = json.load(f)
    
    # نام Release
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    release_name = f"Telegram File - {file_info['filename']}"
    tag_name = f"telegram-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"📦 ایجاد Release: {release_name}")
    
    # دستور gh برای ایجاد Release
    files_path = ' '.join([f'uploaded_files/{f}' for f in files])
    
    cmd = f"""
    gh release create {tag_name} \
      --title "{release_name}" \
      --notes "📥 فایل دانلود شده از تلگرام\\n\\n📊 حجم اصلی: {file_info['size'] / (1024**2):.2f} MB\\n\\n🕐 زمان: {timestamp}\\n\\n📝 تعداد قسمت‌ها: {len(files)}" \
      {files_path}
    """
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Release ایجاد شد: {tag_name}")
        print(f"🔗 لینک: https://github.com/${{GITHUB_REPOSITORY}}/releases/tag/{tag_name}")
    else:
        print(f"❌ خطا: {result.stderr}")
        raise Exception("ایجاد Release ناموفق")

if __name__ == '__main__':
    create_release()
