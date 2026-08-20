import os
import json
import subprocess
from datetime import datetime

def create_release():
    if not os.path.exists('release_files.json'):
        print("❌ release_files.json پیدا نشد")
        return
    
    with open('release_files.json', 'r') as f:
        data = json.load(f)
    
    files = data['parts']
    tag = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    print(f"📤 درحال آپلود Release: {tag}")
    
    # gh release create
    file_args = ' '.join([f"uploaded_files/{f}" for f in files])
    cmd = f"gh release create {tag} {file_args} --generate-notes"
    
    result = os.system(cmd)
    
    if result == 0:
        print(f"✅ Release {tag} آپلود شد!")
    else:
        print(f"❌ خطا در آپلود")
        exit(1)

create_release()
