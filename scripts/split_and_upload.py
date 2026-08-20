import os
import json

CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB

def split_file():
    if not os.path.exists('file_info.json'):
        print("❌ file_info.json پیدا نشد")
        return
    
    with open('file_info.json', 'r') as f:
        info = json.load(f)
    
    filename = info['filename']
    filepath = f"telegram_files/{filename}"
    file_size = info['size']
    
    os.makedirs('uploaded_files', exist_ok=True)
    
    if file_size > CHUNK_SIZE:
        print(f"📦 فایل بزرگ است ({file_size / (1024**2):.2f} MB)")
        print(f"✂️  درحال تقسیم...")
        
        parts = []
        with open(filepath, 'rb') as f:
            part_num = 1
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                part_name = f"{filename}.part{part_num}"
                part_path = f"uploaded_files/{part_name}"
                
                with open(part_path, 'wb') as pf:
                    pf.write(chunk)
                
                parts.append(part_name)
                print(f"✅ Part {part_num} ({len(chunk) / (1024**2):.2f} MB)")
                part_num += 1
        
        # ذخیره لیست
        with open('release_files.json', 'w') as f:
            json.dump({'parts': parts}, f)
        
        print(f"✅ {len(parts)} قسمت ایجاد شد")
    else:
        print(f"✅ فایل کوچک است ({file_size / (1024**2):.2f} MB)")
        os.rename(filepath, f"uploaded_files/{filename}")
        
        with open('release_files.json', 'w') as f:
            json.dump({'parts': [filename]}, f)

split_file()
