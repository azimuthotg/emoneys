# แก้ไข Git Conflict บน Server

## สถานการณ์:
- Server มี uncommitted changes ใน `accounts/pdf_generator.py`
- ไม่สามารถ pull จาก GitHub ได้

## วิธีแก้ไข:

### Option 1: ถ้าการเปลี่ยนแปลงที่ server ไม่สำคัญ (แนะนำ)
```bash
# ดูว่ามีการเปลี่ยนแปลงอะไรที่ server
cd C:\inetpub\wwwroot\emoneys
git diff accounts/pdf_generator.py

# ถ้าการเปลี่ยนแปลงไม่สำคัญหรือซ้ำกับที่ push แล้ว
# ใช้คำสั่งนี้เพื่อยกเลิกการเปลี่ยนแปลง
git checkout -- accounts/pdf_generator.py

# หรือ reset ทั้งหมด (ยกเลิก uncommitted changes ทั้งหมด)
git reset --hard HEAD

# แล้วค่อย pull ใหม่
git pull origin main
```

### Option 2: ถ้าต้องการเก็บการเปลี่ยนแปลงไว้ชั่วคราว
```bash
# Stash การเปลี่ยนแปลงไว้ก่อน
git stash save "temp changes before pull"

# Pull จาก GitHub
git pull origin main

# ถ้าต้องการนำการเปลี่ยนแปลงกลับมา (อาจจะ conflict)
git stash pop
```

### Option 3: ถ้าการเปลี่ยนแปลงที่ server สำคัญ
```bash
# Commit การเปลี่ยนแปลงก่อน
git add accounts/pdf_generator.py
git commit -m "Changes from server"

# แล้ว pull (อาจจะต้อง merge)
git pull origin main
```

## คำแนะนำ:
**ใช้ Option 1** เพราะ:
- เราเพิ่ง push version ล่าสุดไปแล้ว (commit a5b31cb)
- ไฟล์ที่ server น่าจะเป็น version เก่าที่ copy มาก่อนหน้านี้
- การยกเลิกและ pull ใหม่จะได้ version ล่าสุดที่ถูกต้อง

## คำสั่งที่แนะนำ (รันที่ server):
```bash
cd C:\inetpub\wwwroot\emoneys
git status
git diff accounts/pdf_generator.py
git reset --hard HEAD
git pull origin main
python manage.py migrate  # ถ้ามี migration ใหม่
```
