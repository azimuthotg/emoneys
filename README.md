# ระบบใบสำคัญรับเงินอิเล็กทรอนิกส์ (e-Money / edoc_system)

ระบบออกใบสำคัญรับเงินออนไลน์ของ **มหาวิทยาลัยนครพนม (NPU)** — ล็อกอินผ่าน NPU API
(บุคลากรและนักศึกษา) ออกเลขที่เอกสารตามปีงบประมาณไทย สร้าง PDF พร้อม QR code
สำหรับตรวจสอบสาธารณะ และมี workflow ขอแก้ไข/ขอยกเลิกใบสำคัญ

> สถานะ: ใช้งานจริงบน production แล้ว — ดูสถานะงานปัจจุบันที่บล็อก `PROJECT-STATUS`
> ด้านบนของ [CLAUDE.md](CLAUDE.md) และบันทึกความรู้/ปัญหาที่ [MEM.md](MEM.md)

---

## Stack

| ส่วน | เทคโนโลยี |
|---|---|
| Framework | Django 4.2 (Python) |
| ฐานข้อมูล | **MySQL** (utf8mb4) — ไม่ได้ใช้ SQLite |
| Auth | NPU API (`api.npu.ac.th/v2/ldap/`) ผ่าน `HybridAuthBackend` |
| PDF | ReportLab + ฟอนต์ THSarabunNew (มีทางเลือกที่ 2 เรนเดอร์จาก HTML) |
| Frontend | Django Templates + Bootstrap 5 (ไม่มี build step) |
| อื่น ๆ | qrcode, openpyxl (export Excel), django-summernote, pythainlp |

## โครงสร้างโปรเจกต์

```
edoc_system/        settings.py, urls.py (มี /health/ สำหรับ NMS Agent monitoring)
accounts/           แอปเดียวที่ถือทุกอย่างของระบบ
  models.py         17 โมเดล (User, Receipt, DocumentVolume, workflow, audit)
  views.py          view ทั้งหมด (~6,100 บรรทัด)
  backends.py       HybridAuthBackend — auth บุคลากร/นักศึกษา + manual user
  npu_api.py        client เรียก NPU API ฝั่งบุคลากร
  npu_student_api.py  client เรียก NPU API ฝั่งนักศึกษา
  pdf_generator.py  สร้าง PDF ใบสำคัญด้วย ReportLab
  forms.py, admin.py, urls.py
  management/commands/   คำสั่ง Django (สร้าง permission, กำหนด role)
utils/              fiscal_year.py (ปีงบประมาณ/รหัสเล่ม), qr_generator.py, notifications.py
templates/          base_sidebar.html + templates/accounts/ (34 หน้า)
static/fonts/       THSarabunNew 4 น้ำหนัก (ต้องมี ไม่งั้น PDF พัง)
tools/              สคริปต์ซ่อมบำรุงครั้งคราว (ไม่ใช่ส่วนของแอป — ดู tools/README.md)
doc/                ดัชนีเอกสาร + progress log รายวัน (doc/INDEX.md คือจุดเริ่มต้น)
docs/               คู่มือผู้ดูแลระบบ + UML diagrams
```

## ติดตั้งสำหรับพัฒนา

```bash
python -m venv emoney_env && emoney_env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # แล้วกรอกค่า DB และ NPU_API_TOKEN
python manage.py migrate
python manage.py runserver
```

ต้องมี MySQL ที่เข้าถึงได้ตามค่าใน `.env` — ระบบไม่มี fallback เป็น SQLite

### ค่าใน `.env` ที่ขาดไม่ได้

| ตัวแปร | หมายเหตุ |
|---|---|
| `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` | มาตรฐาน Django |
| `BASE_URL` | ใช้ประกอบ URL ใน QR code — ถ้าผิด QR จะชี้ผิดที่ |
| `DB_*` | MySQL |
| `NPU_API_TOKEN` | **token เดียวใช้ทั้งบุคลากรและนักศึกษา** อายุ 365 วัน ต้องต่อมือ |

---

## แนวคิดหลักที่ต้องเข้าใจก่อนแก้โค้ด

### 1. เลขที่ใบสำคัญ — ออกตอน "เสร็จสิ้น" เท่านั้น

รูปแบบ `ddmmyy/xxxx` (เช่น `240968/0001`) สร้างใน `Receipt.save()` **เฉพาะเมื่อ
`status` เปลี่ยนเป็น `completed`** — ใบร่างจึงไม่กินเลข ป้องกันเลขขาดช่วง

เลขวิ่งต่อเนื่องในกลุ่ม **หน่วยงานที่ใช้ `Department.code` เดียวกัน** (กรณีหน่วยงานย่อย
ของสำนักงานอธิการบดีที่แชร์เล่มเดียวกัน) ไม่ใช่แยกตาม department row

### 2. เล่มเอกสาร (DocumentVolume) ผูกกับปีงบประมาณไทย

ปีงบประมาณคือ 1 ต.ค. – 30 ก.ย. คำนวณใน `utils/fiscal_year.py`
รหัสเล่มเป็น `<department code><2 หลักท้ายปีงบ>` เช่น `REG68`
เล่มถูกสร้างอัตโนมัติเมื่อหน่วยงานบันทึกใบแรกของปีงบนั้น

### 3. สิทธิ์เป็น Role → Permission (ไม่ใช่ Django permission)

เช็กด้วย `user.has_permission('...')` ซึ่งวนดูทุก role ที่ active
สามชั้นหลัก:

| ระดับ | สิทธิ์ตัดสิน | เห็นอะไร |
|---|---|---|
| Basic User | — | ใบสำคัญของตัวเองเท่านั้น |
| Department Manager | `receipt_view_department` | ทั้งหน่วยงาน |
| Senior Manager / Admin | `receipt_view_all` | ทั้งระบบ |

`is_superuser` / `is_staff` ผ่านทุกสิทธิ์โดยไม่ตรวจ role

### 4. การล็อกอินมี 3 เส้นทาง

`accounts/backends.py` เรียงลำดับ:

1. username ขึ้นต้นด้วย `admin` → ตรวจรหัสผ่านในเครื่องอย่างเดียว (superuser)
2. ผู้ใช้ `source='manual'` (admin สร้างเอง) → รหัสผ่านในเครื่อง
3. ที่เหลือ → เดาประเภทจากความยาว username (13 หลัก = บุคลากร, 12 หลัก = นักศึกษา)
   ยิง NPU API ฝั่งที่น่าจะใช่ก่อน **ถ้าไม่ผ่านจะลองอีกฝั่งเป็น fallback**

ผู้ใช้ที่มีในฐานข้อมูลแล้ว ถ้า admin ตั้ง "รหัสผ่านสำรอง" ไว้ (`has_usable_password()`)
ระบบจะใช้รหัสนั้นแทนการยิง NPU API

---

## เอกสารประกอบ

- [doc/INDEX.md](doc/INDEX.md) — ดัชนีหลัก + progress log รายวัน (เริ่มที่นี่)
- [MEM.md](MEM.md) — ปัญหา/วิธีแก้/การตัดสินใจเชิงออกแบบ ที่สะสมมา
- [docs/](docs/) — คู่มือผู้ดูแลระบบ และ UML diagrams
- `_archive/` — เอกสารเก่าที่ปลดระวางแล้ว (ไม่อยู่ใน git, **อย่าใช้อ้างอิง** เนื้อหาไม่ตรงกับระบบปัจจุบัน)
