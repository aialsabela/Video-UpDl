import os
import json
import subprocess
from datetime import datetime

def create_release():
    with open('release_files.json', 'r') as f:
        release_data = json.load(f)
    
    # تگ با تاریخ
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    tag_name = f"release-{timestamp}"
    
    print(f"📦 ایجاد Release: {tag_name}")
    
    # دستورات آپلود
    upload_files = []
    for part in release_data['parts']:
        upload_files.append(f"uploaded_files/{part}")
    
    # ایجاد Release
    cmd = ['gh', 'release', 'create', tag_name]
    cmd.extend(upload_files)
    cmd.extend(['--title', f"Telegram Files - {timestamp}"])
    cmd.extend(['--notes', f"Original: {release_data['original_filename']}\nSize: {release_data['original_size'] / 1024 / 1024:.2f} MB\nParts: {release_data['part_count']}"])
    
    print(f"▶️  دستور: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Release ایجاد شد")
        print(result.stdout)
    else:
        print(f"❌ خطا:")
        print(result.stderr)
        raise Exception("Release creation failed")

if __name__ == '__main__':
    create_release()
