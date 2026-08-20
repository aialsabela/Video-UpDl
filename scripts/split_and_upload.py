import os
import json

CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB

def split_file(filepath):
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    
    print(f"📊 اندازه فایل: {file_size / 1024 / 1024:.2f} MB")
    
    if file_size <= CHUNK_SIZE:
        print("✅ فایل کوچک است، تقسیم نیازی نیست")
        return [filename]
    
    print(f"📂 تقسیم به قطعات {CHUNK_SIZE / 1024 / 1024:.0f} MB...")
    
    os.makedirs('uploaded_files', exist_ok=True)
    parts = []
    
    with open(filepath, 'rb') as f:
        part_num = 1
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            part_filename = f"{filename}.part{part_num}"
            part_path = f"uploaded_files/{part_filename}"
            
            with open(part_path, 'wb') as part_file:
                part_file.write(chunk)
            
            parts.append(part_filename)
            print(f"  ✅ {part_filename}")
            part_num += 1
    
    print(f"✅ تقسیم کامل: {len(parts)} قطعه")
    return parts

if __name__ == '__main__':
    with open('file_info.json', 'r') as f:
        metadata = json.load(f)
    
    filepath = f"telegram_files/{metadata['filename']}"
    parts = split_file(filepath)
    
    release_data = {
        'original_filename': metadata['filename'],
        'original_size': metadata['size'],
        'parts': parts,
        'part_count': len(parts)
    }
    
    with open('release_files.json', 'w') as f:
        json.dump(release_data, f, indent=2)
    
    print(f"📋 لیست قطعات ذخیره شد")
