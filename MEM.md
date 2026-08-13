# MEM.md — คลังความรู้โปรเจกต์ emoneys

บันทึกปัญหา/วิธีแก้/การตัดสินใจเชิงออกแบบของโปรเจกต์นี้ ทะเบียนงาน (สถานะ + งานที่ต้องทำ)
อยู่ที่บล็อก `PROJECT-STATUS` ใน [CLAUDE.md](CLAUDE.md)

---

## ปัญหา & วิธีแก้

### 2026-06-20 — นักศึกษา login ไม่ได้ แต่บุคลากรได้ปกติ

**อาการ** นักศึกษาล็อกอินไม่ผ่าน บุคลากรใช้งานปกติ

**ต้นตอ** ตอนนั้น `.env` แยก JWT เป็น 2 ตัว — `NPU_API_TOKEN` (endpoint `auth_and_get_personnel/`)
กับ `NPU_STUDENT_API_TOKEN` (endpoint `auth_and_get_student/`) token หมดอายุพร้อมกัน 2026-06-18
แต่ตอนต่ออายุ update แค่ฝั่งบุคลากร ลืมฝั่งนักศึกษา → NPU API ตอบ `401 "token not valid"`
ยืนยันจาก log ฝั่ง NPU ที่ `/monitor/api-usage/` (auth_and_get_student = 401, personnel = ผ่าน)
โค้ด client แนบ Bearer header ถูกต้องอยู่แล้ว ไม่ใช่บั๊กโค้ด

**วิธีแก้** (commit `c08b6dc`) รวมเหลือ token เดียว — สอง endpoint อยู่บน NPU API ตัวเดียวกัน
รับ JWT ตัวเดียวกันได้ ใน `edoc_system/settings.py` ตั้ง `NPU_STUDENT_API_TOKEN = NPU_API_TOKEN`
ตรง ๆ (ไม่อ่านจาก `.env` แล้ว) และเอาตัวแปรนั้นออกจาก `.env.example`

**บทเรียน** ความลับที่ต้องต่ออายุ อย่าเก็บไว้หลายที่ — จุดต่ออายุที่ซ้ำกันคือจุดที่จะลืม
ถ้าแก้ token บน prod ต้อง **restart แอป** ด้วย เพราะ header ถูกประกอบตอนโหลด settings

### 2026-08-13 — เอกสารในโปรเจกต์พาหลงทาง

**อาการ** โปรเจกต์มี `.md` ที่ root 26 ไฟล์ หลายไฟล์ขัดแย้งกันเอง เปิดอ่านแล้วเข้าใจระบบผิด

ตัวอย่างที่ผิดจริง:
- `README.md` เดิม อธิบายระบบ login แบบอ่าน CSV + MD5 ซึ่งเลิกใช้ไปนานแล้ว
- `CODEBASE_ANALYSIS.md` / `PROJECT_PROGRESS.md` เขียนว่าเป็นของ "มหาวิทยาลัยราชภัฏนครราชสีมา"
  (จริงคือ **มหาวิทยาลัยนครพนม**) และบอกว่าใช้ SQLite (จริงคือ MySQL)
- `FILE_REFERENCE_GUIDE.md` อ้างเลขบรรทัดที่เลื่อนไปหมดแล้ว และใช้ path แบบ `/mnt/c/...`
- `NPU_LOGIN_SYSTEM_GUIDE.md` อธิบายไฟล์ `accounts/decorators.py` ที่ไม่มีอยู่ในโปรเจกต์

**วิธีแก้** ย้ายทั้งหมดไป `_archive/` (เพิ่มใน `.gitignore`) พร้อม `_archive/README.md`
ที่ระบุชัดว่าห้ามใช้อ้างอิง เขียน `README.md` ใหม่จากการอ่านโค้ดจริง และประกาศใน `CLAUDE.md`
ว่าอย่าอ่าน `_archive/` เหลือแหล่งอ้างอิงจริงแค่ `README.md` / `MEM.md` / `doc/INDEX.md`

---

## บั๊กที่รู้แล้วแต่ยังไม่แก้

### race condition ตอนออกเลขที่ใบสำคัญ

`Receipt.generate_receipt_number()` ([accounts/models.py:1254](accounts/models.py))
เปิด `transaction.atomic()` ครอบแค่ตอนอ่าน `Max(receipt_number)` **แล้วปิดบล็อกก่อน
`super().save()` จะ INSERT จริง** — lock ถูกปล่อยไปก่อนแถวใหม่จะถูกเขียน
ยิ่ง `select_for_update().aggregate()` ไม่ได้ล็อกอะไรที่เป็นประโยชน์ เพราะแถวที่แย่งกัน
ยังไม่มีอยู่ (MySQL ต้องใช้ gap lock)

**อย่าอธิบายบั๊กนี้แบบเหมารวมว่า "กดพร้อมกันแล้วเลขซ้ำ"** — มีตาข่ายรองรับอยู่ 2 ชั้น:

1. DB มี `unique_together = (receipt_number, department)` บน `Receipt`
2. `receipt_save_ajax` ดัก `IntegrityError` แล้วตอบ 409 "เลขที่ใบสำคัญซ้ำ กรุณาลองใหม่อีกครั้ง"
   ([accounts/views.py:1884](accounts/views.py))

ผลจริงจึงเป็น:

| กรณี | ผลลัพธ์ |
|---|---|
| หน่วยงานเดียวกัน ผ่าน `receipt_save_ajax` | DB ปฏิเสธ → ผู้ใช้เห็นข้อความให้ลองใหม่ ข้อมูลไม่เสีย |
| **คนละ department ที่ใช้ `code` เดียวกัน** | constraint ไม่ยิงเพราะ department ต่างกัน → **เลขซ้ำจริงในเล่มเดียวกัน** |
| ผ่าน `receipt_complete_draft_ajax` | `receipt.save()` เปล่า ๆ ไม่ดัก IntegrityError → 500 |

รูรั่วจริงเหลือแค่แถวกลาง — วัดจากฐาน test (`emoneys_testPO`) มีรหัสที่แชร์กันแค่
`PO` (4 หน่วยงาน) กับ `EDU` (2) และยังไม่มีเลขซ้ำเลยใน 112 ใบ
โอกาสเกิดต่ำแต่ผลกระทบสูงเพราะเป็นเอกสารการเงิน

**แนวทางแก้ที่ตกลงกันไว้:** ย้ายตัวนับไปอยู่บนแถว `DocumentVolume` แล้ว `select_for_update()`
แถวนั้น (ล็อกแถวที่มีอยู่จริง ได้ผล) พร้อมขยาย atomic ให้ครอบถึง INSERT
และเพิ่มการดัก IntegrityError ใน `receipt_complete_draft_ajax` ด้วย

### last_document_number นับไม่ตรงกับตอนออกเลข

ตอนอัปเดตหลังบันทึก ([accounts/models.py:1205](accounts/models.py)) กรองด้วย
`department=self.department` ตัวเดียว แต่ตอนออกเลขกรองด้วย **ทุก department ที่ใช้ `code` เดียวกัน**
→ เล่มที่หลายหน่วยงานแชร์กัน ค่านี้จะต่ำกว่าความจริง (กระทบหน้าเลขเอกสาร/รายงาน ไม่กระทบเลขที่ออกจริง)

### Permission choices หลุด sync

`receipt_cancel_approve` และ `receipt_cancel_approve_manager` ถูกเรียกใช้ใน views/models
และถูกสร้างลง DB โดย `create_permissions.py` แต่ **ไม่มีใน `Permission.PERMISSION_TYPES`**
ระบบทำงานได้ (Django choices เป็นแค่ validation) แต่ dropdown ใน admin จะไม่มีตัวเลือกนี้
และ `full_clean()` จะไม่ผ่าน

---

## การตัดสินใจ

### 2026-08-13 — `_archive/` แทนการลบทิ้ง

เลือกย้ายเข้า `_archive/` + gitignore แทน `git rm` เพราะกู้ได้ทั้งจากดิสก์และ git history
ขณะที่ AI และคนอ่านใหม่จะไม่เจอมันจาก root อีก ได้ผลเหมือนลบแต่ย้อนได้

### 2026-08-13 — เก็บ 3 สคริปต์ไว้ใน `tools/`

`seed_templates.py`, `fix_missing_volumes.py`, `update_volume_counts.py` ยังใช้ซ่อมข้อมูลจริงได้
จึงคง track ไว้ใน `tools/` พร้อม README ที่บอกความเสี่ยงของแต่ละตัว
ที่เหลือ (debug/ตรวจข้อมูล/ลบข้อมูลทดสอบ ~32 ไฟล์) เข้า `_archive/scripts/`
โดยเฉพาะชุด reset receipts ที่อันตรายแล้วเพราะระบบขึ้น production ไปแล้ว —
รันตอนนี้คือลบข้อมูลจริง

### เลขที่ใบสำคัญออกตอน "เสร็จสิ้น" เท่านั้น

ใบร่างไม่กินเลข เพื่อไม่ให้เกิดเลขขาดช่วงเมื่อผู้ใช้สร้างร่างแล้วทิ้ง
ผลข้างเคียงคือ `receipt_number`, `verification_hash`, `qr_code_data` เป็น null ในสถานะร่าง
โค้ดที่แตะฟิลด์พวกนี้ต้องเผื่อกรณี null เสมอ

### เลขวิ่งต่อเนื่องตาม `Department.code` ไม่ใช่ตาม department row

หน่วยงานย่อยของสำนักงานอธิการบดีใช้รหัสหน่วยงานเดียวกันและต้องแชร์เล่ม/เลขเดียวกัน
`get_or_create_volume_for_department()` จึงหา volume จาก `volume_code + fiscal_year` ก่อน
แล้วค่อย fallback ไปสร้างใหม่ — ห้ามเปลี่ยนกลับไปหาโดย `department` ตรง ๆ

---

## Production — ตรวจสอบจริงบนเครื่อง 13 ส.ค. 2569

ตรวจด้วย PowerShell บนเครื่อง prod เอง ไม่ได้อ่านจากเอกสารเก่า

| หัวข้อ | ค่าจริง |
|---|---|
| path | **`C:\emoneys`** |
| URL | `http://110.78.83.103/` — HTTP ผ่าน IP ตรง ไม่มี domain ไม่มี HTTPS ไม่มี reverse proxy |
| วิธีรัน | `python -m waitress --listen=0.0.0.0:80 edoc_system.wsgi:application` |
| auto-start | **Windows Service ชื่อ `emoneys`** — Running, StartType Automatic (reboot แล้วขึ้นเอง) |
| DB | `emoneys` @ **`110.78.83.103`** — เครื่องเดียวกันแต่ต่อผ่าน public IP ไม่ใช่ localhost |
| ปริมาณข้อมูล | ใบสำคัญ completed **10,484 ใบ**, 25 หน่วยงาน |
| deploy | `git pull` บนเครื่องตรง ๆ ไม่มี CI/CD |

> ⚠️ **`deploy_path` ที่เคยจดไว้ผิดทั้ง 2 แหล่ง** — เอกสารเก่า พ.ย. 2568 เขียน `C:\inetpub\wwwroot\emoneys`
> และ `nms_agent/docs/projects/emoneys.md` เขียน `C:\projects\emoneys` ของจริงคือ `C:\emoneys`

### ⚠️ prod รันด้วย `DEBUG=True` และแก้ตรง ๆ ไม่ได้

ยืนยันแล้วจาก settings ที่มีผลจริง: `DEBUG=True`, `SECURE_SSL_REDIRECT=False`,
`ALLOWED_HOSTS=['localhost','127.0.0.1','110.78.83.103']`, `EMAIL_BACKEND=console`

**ห้ามสลับเป็น `DEBUG=False` เฉย ๆ** จะพัง 2 ต่อ:

1. **static หาย** — [edoc_system/urls.py:51](edoc_system/urls.py) เสิร์ฟ static/media ในบล็อก
   `if settings.DEBUG:` เท่านั้น Waitress ไม่ได้เสิร์ฟไฟล์นิ่งเอง และไม่มี IIS/nginx อยู่หน้า
   → CSS/JS/โลโก้ 404 หมด (มีโฟลเดอร์ `staticfiles` อยู่แล้ว แปลว่าเคย `collectstatic`)
2. **เข้าเว็บไม่ได้** — `SECURE_SSL_REDIRECT` จะกลายเป็น `True` ตามบล็อก `if not DEBUG:`
   ใน settings แล้ว redirect ไป https ที่ไม่มีอยู่

ที่ `SECURE_SSL_REDIRECT=False` อยู่ตอนนี้ **เป็นผลพลอยได้จาก DEBUG=True ไม่ใช่การตั้งใจตั้งค่า**

**ลำดับการแก้ที่ปลอดภัย:** ติดตั้ง `whitenoise` + เพิ่ม middleware → ย้าย `SECURE_SSL_REDIRECT`
ออกมาตั้งเป็น `False` อย่างชัดเจนแทนที่จะผูกกับ DEBUG → ค่อยตั้ง `DEBUG=False` → ทดสอบ static

**ความเสี่ยงระหว่างที่ยังไม่แก้:** หน้า error 500 ของ Django ตอน DEBUG=True แสดงค่า settings
ทั้งหมดรวม `SECRET_KEY`, รหัส MySQL และ NPU API token ให้คนที่ทำให้เกิด error เห็น
บนระบบที่เปิด HTTP สาธารณะทาง IP และ MySQL ก็ผูกกับ public IP ด้วย

### สภาพแวดล้อม Python บนเครื่องยังไม่ชัด (ค้างตรวจ)

พบ Waitress รันอยู่ **2 process** สั่ง bind `0.0.0.0:80` เหมือนกัน:
`C:\emoneys\emoney_env\Scripts\python.exe` (PID 3568) และ **`C:\Python312\python.exe`** (PID 3600)
ทั้งที่ port 80 ผูกได้แค่ตัวเดียว

และ `emoney_env\Scripts\python.exe -m pip list` ไม่เจอ Django/waitress/mysqlclient เลย
ทั้งที่ interpreter ตัวเดียวกัน `import django` ได้ปกติ — อาจเป็นเพราะ venv ไม่มี pip
หรือถูกสร้างแบบ `--system-site-packages` แล้วดึงของจาก `C:\Python312`

**ต้องเคลียร์ก่อนแตะ dependency ใด ๆ** (เช่นตอนติดตั้ง whitenoise) ไม่งั้นอาจ install ลง venv
แล้วตัวที่รันจริงไม่เห็น

---

## หมายเหตุ

- **ฐานข้อมูลคือ MySQL เท่านั้น** ไม่มี fallback SQLite (ในโค้ด settings คอมเมนต์ไว้แต่ไม่ได้เปิด)
- `data/users.csv` + `_authenticate_with_file()` ใน `backends.py` เป็นซากระบบ login แบบไฟล์เดิม
  ไม่มีเส้นทางไหนเรียกถึงแล้ว แต่ยังไม่ได้ลบ
- `EMAIL_BACKEND` เป็น `console` แม้บน production → อีเมลแจ้งเตือนปีงบประมาณไม่ออกจริง
- `pywebpush` อยู่ใน requirements และ `User` มีฟิลด์ push subscription แต่ **ไม่มีโค้ดส่งเลย**
- username ที่ขึ้นต้นด้วย `admin` จะข้าม NPU API ทั้งหมดไปเช็กรหัสผ่านในเครื่อง
  ([accounts/backends.py:42](accounts/backends.py)) — จงใจให้ superuser เข้าได้ตอน API ล่ม
- ฟอนต์ `static/fonts/THSarabunNew*.ttf` ขาดไม่ได้ ถ้าหายไป PDF จะพัง
- remote git URL เคยฝัง GitHub PAT — **ตรวจ 13 ส.ค. 2569 แล้วสะอาดแล้ว** ไม่มี token ใน `.git/config`
  และ `.env` อยู่ใน `.gitignore` ถูกต้อง
