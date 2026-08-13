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

### 2026-08-13 — ต่อ MySQL prod จากข้างนอกไม่ได้ (`ERROR 1129` host is blocked)

**อาการ** DBeaver จากเครื่องนอก prod ขึ้น
`Host '110.78.83.1' is blocked because of many connection errors`

**ต้นตอ** ทุก connection จากนอกเครื่องถูก NAT ยุบเป็น IP เดียว (`110.78.83.1` = gateway ของ
subnet `110.78.83.0/25`) MySQL จึงนับ error ของทุกคนรวมกันในถังเดียว พอชน
`max_connect_errors` = **100** (ค่า default) ก็บล็อก → **คนนอกเข้าไม่ได้พร้อมกันทั้งหมด**

ยืนยันจาก `performance_schema.host_cache`: `SUM_CONNECT_ERRORS = COUNT_HANDSHAKE_ERRORS = 101`
พอดีตัว = **เป็น handshake error ล้วน 100%** ไม่ใช่ DNS (`NAMEINFO_PERMANENT` แค่ 1 และ error
ชนิด permanent ไม่ถูกนับเข้าโควตา) และไม่ใช่รหัสผ่านผิด — แถวของ `110.78.83.103` มี
`AUTHENTICATION_ERRORS = 4` แต่ `SUM_CONNECT_ERRORS = 0` **พิสูจน์ว่า auth error ไม่ทำให้โดนบล็อก**

**ไม่กระทบเว็บ** เพราะแอปต่อ DB จาก `110.78.83.103 → 110.78.83.103` วนในเครื่อง
(NIC ถือ public IP ตัวนี้โดยตรง) ไม่ผ่าน NAT

**วิธีแก้** `FLUSH HOSTS;` ด้วยสิทธิ์ root — ล้าง cache ในหน่วยความจำ ไม่แตะข้อมูล ไม่ต้อง restart

**ยังไม่แก้ต้นเหตุ** `max_connect_errors` ยังเป็น 100 → จากสถิติจริง ~17 handshake error/วัน
**จะกลับมาโดนบล็อกอีกในราว 6 วัน** เคยเกิดมาแล้ว 4 รอบ (4 มิ.ย. / 17 มิ.ย. / 20 ก.ค. / 7 ส.ค. 2569)

**บทเรียน** อย่าด่วนสรุปสาเหตุจากข้อความ error — ตอนแรกเดาว่าเป็น DNS เพราะเห็น log
`IP address '110.78.83.1' could not be resolved` แต่ตัวเลขใน `host_cache` ชี้ไปที่ handshake
คนละเรื่องกัน และเดาว่าบอตสแกนจากอินเทอร์เน็ต ซึ่งก็ผิด — `host_cache` มีแค่ 2 แถวจากที่จุได้ 279
แปลว่าไม่มีใครจากข้างนอกยิงเข้ามาเลยนอกจากผ่าน NAT ตัวนั้น

รายละเอียดครบ + แผนย้อนกลับอยู่ที่ [doc/runbook-mysql-host-blocked.md](doc/runbook-mysql-host-blocked.md)

---

### 2026-08-13 — ผู้ใช้ย้ายหน่วยงานแล้วระบบยังโชว์หน่วยงานเดิม

**อาการ** บุคลากรย้ายจากคณะเทคโนโลยีอุตสาหกรรมไปวิทยาลัยพยาบาลบรมราชชนนีนครพนม
แต่หน้าจัดการผู้ใช้ยังแสดงหน่วยงานเดิม

**ต้นตอ** `_create_staff_user()` ([backends.py](accounts/backends.py)) เขียน `department`
จาก NPU API **ตอนสร้างบัญชีครั้งเดียว** ส่วน `_check_database_staff()` ซึ่งเป็นเส้นทาง login
ครั้งต่อ ๆ ไป ตรวจแค่รหัสผ่านกับอัปเดต `last_login` **ไม่เคย sync ข้อมูลใหม่เลย**

ยืนยันจากข้อมูลจริง: user id 34 มี `last_npu_sync = 2025-10-31 07:29:01` เท่ากับ `date_joined`
เป๊ะ แต่ `last_login = 2026-08-06` — เข้าระบบมา 9 เดือนโดยข้อมูลไม่ขยับ
ผู้ใช้ `npu_api` **ทั้ง 1,352 คน** (staff 535 + student 817) อยู่ในสภาพเดียวกันหมด

**ปัญหาซ้อน** ปุ่มแก้ไขข้อมูลใน `user_management.html` ครอบด้วย `{% if user.source == 'manual' %}`
→ แก้ได้เฉพาะผู้ใช้ manual 48 คน ที่เหลือ 1,352 คนไม่มีทางแก้ผ่านหน้าเว็บเลย

**วิธีแก้** (commit `9a82ea2`) เพิ่มปุ่ม "ดึงข้อมูลจาก NPU ใหม่" ใน modal ดูรายละเอียด
ดูหัวข้อ "ปุ่ม re-sync ข้อมูล NPU รายคน" ใน `## การตัดสินใจ`

**บทเรียน** ตอนแรกผมสรุปว่าทำ re-sync ไม่ได้ เพราะดูแค่ endpoint ที่โค้ดตั้งค่าไว้
(`auth_and_get_personnel/` ที่บังคับต้องมีรหัสผ่าน) แล้วเหมาว่า API ไม่มีทางอื่น
ของจริง NPU มี endpoint lookup ที่ใช้ JWT อย่างเดียวอยู่แล้ว
**อย่าสรุปความสามารถของ API ภายนอกจากโค้ดที่เราเขียนไว้ — ไปดูเอกสารของเขาจริง ๆ**

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

### 2026-08-13 — ปุ่ม re-sync ข้อมูล NPU รายคน (แทนการทำหน้าแก้ไขด้วยมือ)

เลือกทำ **ปุ่มดึงข้อมูลจาก NPU** แทน **หน้าฟอร์มให้แอดมินพิมพ์แก้เอง** ที่วางแผนไว้ตอนแรก
เพราะดึงจากต้นทางที่เป็นเจ้าของข้อมูลจริง ไม่มีโอกาสพิมพ์ผิด/เลือกหน่วยงานผิด
และถ้ามีทั้ง 2 ทาง ค่าที่แก้มือจะขัดกับ NPU แล้วถูกเขียนทับตอน sync ครั้งถัดไป

**หน้าแก้ไขเดิม (`manual_user_edit_view`) ไม่ถูกแตะเลย** ยังเป็นของผู้ใช้ manual ต่อไป
ซึ่งถูกต้องแล้ว เพราะผู้ใช้ manual ไม่มีต้นทาง NPU ให้ดึง

#### endpoint ที่ใช้ (ทดสอบจริงบน prod แล้ว 13 ส.ค. 2569)

```
GET https://api.npu.ac.th/v2/personnel/{staffcitizenid}/    → HTTP 200
GET https://api.npu.ac.th/v2/student/{student_code}/        → HTTP 200
Authorization: Bearer <JWT ตัวเดียวกับ NPU_API_TOKEN>
```

**ยืนยันสิทธิ์ด้วย JWT อย่างเดียว ไม่ต้องใช้รหัสผ่านของเจ้าตัว** — นี่คือเหตุผลที่ทำ re-sync ได้

⚠️ **อยู่คนละ path กับ endpoint auth** — auth อยู่ใต้ `/v2/ldap/` แต่ lookup อยู่ใต้ `/v2/` ตรง ๆ
จึงต้องมี setting แยกคือ `NPU_API_LOOKUP_BASE_URL` (มี default ใน settings.py แล้ว
prod ไม่ต้องแก้ `.env`)

response เป็น JSON **แบบแบน** ต่างจาก endpoint auth ที่ห่อด้วย `success`/`personnel_info`
แต่ **ชื่อฟิลด์ข้างในเหมือนกันทุกตัว** จึงห่อให้เป็นรูปเดียวกันแล้วส่งต่อให้
`extract_user_data()` / `extract_student_data()` เดิมได้เลย ไม่ต้องเขียน mapper ใหม่

#### สิ่งที่กันไว้ในโค้ด

- เขียนเฉพาะฟิลด์ใน whitelist (`NPU_RESYNC_FIELDS_STAFF` / `_STUDENT` ใน views.py)
  **ไม่แตะ** `username` / `ldap_uid` / `student_code` (คีย์ระบุตัวตน ถ้าเปลี่ยนคนนั้น login ไม่ได้),
  `approval_status` / `is_active` / บทบาท (เป็นเรื่องของระบบเรา ไม่ใช่ของ NPU)
  และ `npu_last_login` (endpoint lookup ไม่ได้คืนมา ถ้าเขียนทับข้อมูลเดิมจะหาย)
- **ค่าว่างจาก NPU แปลว่า "ไม่มีข้อมูล" ไม่ใช่ "ให้ลบทิ้ง"** จึงข้ามไป ไม่เขียนทับของเดิม
- เตือนถ้าหน่วยงานใหม่ยังไม่มีในตาราง `Department` เพราะระบบจับคู่ด้วย**ชื่อตรงเป๊ะ**
  ถ้าไม่มีแถวรองรับ ผู้ใช้จะออกใบสำคัญไม่ได้ (ตอนนี้ orphan = 0 ต้องรักษาไว้)
- GET = พรีวิว ไม่เขียนฐาน / POST = เขียนจริง — แอดมินเห็นตารางเทียบก่อนยืนยันเสมอ
- บันทึกลง `UserActivityLog` action `npu_resync` ว่าใครสั่งและเปลี่ยนอะไรจากอะไรเป็นอะไร

#### ทำไมใบสำคัญเก่าไม่กระทบ — **พิสูจน์ด้วยการรันจริงบนสำเนา production แล้ว**

`Receipt.department` เป็น **FK ที่บันทึกไว้ตอนสร้างใบ** ไม่ได้อ้างสังกัดปัจจุบันของผู้สร้าง
เปลี่ยน `User.department` แล้วใบเก่าไม่ขยับ รายงานย้อนหลังตรงตลอดไป

**การทดสอบ (13 ส.ค. 2569)** import สำเนา prod ทั้งฐาน (11,523 ใบ / 1,400 ผู้ใช้) ลง
MySQL container แล้วรัน resync ผู้ใช้ id 34 จริง (เทคโนฯ → วิทยาลัยพยาบาล)
ใช้ใบจริงเลขที่ `190126/0001` (id 3195, completed, `department_id = 7`)
เก็บภาพทุกพื้นผิวก่อน/หลังแล้วเทียบทีละบรรทัด:

| พื้นผิว | ผลต่าง |
|---|---|
| หน้ารายละเอียดใบ | ต่างแค่ CSRF token 4 ตัว — เนื้อหาไม่ต่างสักตัวอักษร |
| PDF v1 (reportlab, ตัวที่ผู้ใช้กดพิมพ์จริง) | ข้อความ 351 โทเคน **เหมือนกันทุกตัว** ไบต์ตรงกันหลังตัด CreationDate/ModDate/ID |
| PDF v2 (HTML) | **เหมือนกันทุกตัวอักษร** (diff = 0 บรรทัด) |
| หน้าตรวจสอบสาธารณะ (QR) | **เหมือนกันทุกตัวอักษร** |
| รายการใบสำคัญ / รายงาน | ต่างแค่ CSRF token |
| `accounts_receipt.department_id` | ยังเป็น **7** เหมือนเดิม |

⚠️ **แต่เจอบั๊กที่มีอยู่ก่อนแล้วระหว่างทดสอบ** — `receipt_pdf_v2.html` บรรทัด 258 กับ 292
เขียน `{{ receipt.created_by.department.name }}` ซึ่งดึงหน่วยงาน**ปัจจุบันของคน** ไม่ใช่ของใบ
ตอนนี้มัน render เป็น **ค่าว่าง** (ยืนยันแล้วจากการรันจริง ทั้งก่อนและหลัง resync)
เพราะ `User.department` เป็น `CharField` พอต่อ `.name` เข้าไป Django หา attribute ไม่เจอ
→ หัวกระดาษกับช่อง "ได้รับเงินจาก" ใน PDF v2 ว่างเปล่าอยู่

**ห้ามแก้ด้วยการตัด `.name` ออกเฉย ๆ** จะกลายเป็นดึงข้อมูลสดทันที แล้วใบเก่าทุกใบ
จะเปลี่ยนหน่วยงานตามคนสร้าง ต้องแก้เป็น `{{ receipt.department.name }}` เท่านั้น

พิสูจน์แล้วว่ามันคืนค่าว่าง **ทุกกรณีที่เป็นไปได้** (ข้อความปกติ / ว่าง / `None` /
แม้แต่ข้อความที่เขียนว่า `name`) เพราะข้อความไม่มี attribute ชื่อ `name`
และ `string_if_invalid` ไม่ได้ตั้งไว้ → default `''`
**เคสเดียวที่มันจะตื่นขึ้นมาคือถ้ามีคนเปลี่ยน `User.department` จาก CharField เป็น ForeignKey**

### ⚰️ PDF v2 เป็นโค้ดตาย — อย่าเสียเวลาแก้เทมเพลตนี้

ตรวจเมื่อ 13 ส.ค. 2569:

| ตรวจ | ผล |
|---|---|
| ปุ่มที่เรียก `printReceiptV2()` / `downloadPDFV2()` | **ไม่มีเลย** ฟังก์ชันถูกประกาศใน `receipt_detail.html` แต่ไม่มีใครเรียก |
| `pdfkit` บน prod | **ไม่มี** — `ModuleNotFoundError` |
| `pdfkit` ใน `requirements.txt` | **ไม่อยู่** |
| `wkhtmltopdf.exe` | มีที่ `C:\Program Files\wkhtmltopdf\bin\` แต่ไม่มีตัวเรียก |
| `reportlab` | ✅ 4.4.4 — **นี่คือตัวที่สร้าง PDF จริง** ผ่าน `pdf_generator.py` |

ยิง `/receipt/<id>/pdf/v2/` ตรง ๆ ก็ได้แค่ error แล้วเด้งกลับ `receipt_list`
([views.py:2228](accounts/views.py) จับ `Exception` ทั้งหมด)

**ถ้าจะลบ element ทิ้ง ระวัง layout ขยับ** (กรณีมีคนปลุก PDF v2 ขึ้นมาภายหลัง):
`.dept-name` มี `margin: 0 0 10px 0` และ `.form-value` มี `border-bottom: 1px dotted`
ซึ่งคือเส้นประหลังคำว่า "ได้รับเงินจาก" — ลบ span ทิ้งแล้วเส้นประหายไปด้วย

**ข้อมูลที่ยังเป็น "ของสด" จริง ๆ คือชื่อผู้สร้าง** (`receipt.created_by.get_display_name()`)
ใช้ในหน้ารายละเอียด/ตรวจสอบสาธารณะ และใน PDF v1 เฉพาะกรณี `is_loan=True`
ถ้า NPU เปลี่ยนชื่อคน (เช่น เปลี่ยนคำนำหน้า) ใบเก่าจะโชว์ชื่อใหม่ — ไม่ได้ทดสอบเคสนี้
เพราะชื่อไม่เปลี่ยน แต่รู้จากการอ่านโค้ด
และผู้ใช้ระดับ Basic User มองเห็นใบด้วย `created_by=user` ไม่ใช่หน่วยงาน
(สิทธิ์ `basic_user` มี 8 ตัว ไม่มี `receipt_view_department` / `receipt_view_all` / `report_view`)
→ ย้ายหน่วยงานแล้วเขาไม่เห็นใบเก่าของหน่วยงานใหม่ และไม่เสียใบเก่าของตัวเอง

**ข้อยกเว้น**: `department_manager` (30 คน) กับ `senior_manager` (3 คน) มองเห็นระดับหน่วยงาน
ย้ายสังกัดแล้วขอบเขตที่เห็นจะเปลี่ยนทันที

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

### โครงสร้าง process — มีเซิร์ฟเวอร์ตัวเดียว (อย่าตกใจตอนเห็น python 2 ตัว)

```
services.exe → nssm.exe (C:\nssm\win64\nssm.exe, LocalSystem)
                 └─ python.exe  C:\emoneys\emoney_env\Scripts\python.exe   ← venv launcher
                      └─ python.exe  C:\Python312\python.exe               ← ตัวที่ถือ port 80
```

`Get-CimInstance Win32_Process` จะโชว์ python 2 ตัวที่มี command line เหมือนกันเป๊ะ
(`-m waitress --listen=0.0.0.0:80 edoc_system.wsgi:application`) **ไม่ใช่ของหลงเหลือ 2 ชุด** —
เป็นคู่ parent/child ปกติของ venv บน Windows ที่ `Scripts\python.exe` ไป exec interpreter จริงที่
`C:\Python312` โดยยังคง `sys.prefix` ของ venv ไว้ ยืนยันจาก `ParentProcessId` และเวลาสร้างที่ตรงกัน

NSSM ตั้งค่าไว้ถูกต้อง: `Application = C:\emoneys\emoney_env\Scripts\python.exe`,
`AppDirectory = C:\emoneys` → **ระบบรันจาก venv จริง** ไม่ได้ข้ามไปใช้ system Python

### venv ไม่มี pip

`emoney_env` เป็น venv ที่แยกขาดปกติ (`include-system-site-packages = false`) และมี
Django 4.2.25 ที่ `C:\emoneys\emoney_env\Lib\site-packages` ครบ **แต่ `python -m pip list` ไม่คืนอะไรเลย**
แปลว่าไม่มี pip ในนั้น

ก่อนจะติดตั้งอะไร (เช่น `whitenoise` ตอนแก้ DEBUG) ต้องกู้ pip ก่อน:
`.\emoney_env\Scripts\python.exe -m ensurepip --upgrade`

### NSSM รันด้วยสิทธิ์ LocalSystem

`StartName = LocalSystem` — สูงกว่าที่เว็บแอปต้องการมาก ถ้าแอปมีช่องโหว่ ผู้โจมตีได้สิทธิ์สูงสุด
ของเครื่องทันที ควรเปลี่ยนเป็น service account เฉพาะที่มีสิทธิ์เท่าที่จำเป็น (ไม่ด่วน)

### SSH เข้า prod ได้แล้ว (13 ส.ค. 2569)

เดิมเข้าได้ทาง RDP อย่างเดียว ตอนนี้ติดตั้ง OpenSSH Server แล้ว

| หัวข้อ | ค่า |
|---|---|
| ปลายทาง | `Administrator@110.78.83.103` (Windows Server 2022, build 20348) |
| private key | `C:\Users\azimuthotg\.ssh\emoneys_prod` — ed25519 **ไม่มี passphrase** |
| public key อยู่ที่ | `C:\ProgramData\ssh\administrators_authorized_keys` บน prod |
| service | `sshd` StartupType Automatic |

**จุดที่พลาดกันบ่อยตอนตั้ง** (เจอมาแล้วทั้งคู่):

1. บัญชีที่อยู่ในกลุ่ม Administrators **ไม่ใช้** `~\.ssh\authorized_keys` ต้องใส่ที่
   `C:\ProgramData\ssh\administrators_authorized_keys` และตั้ง ACL ให้เหลือแค่
   SYSTEM + Administrators (`icacls ... /inheritance:r`) ไม่งั้น sshd เมินไฟล์ทั้งไฟล์แบบเงียบ ๆ
2. เขียนไฟล์ด้วย `-Encoding utf8` บน PowerShell 5.1 จะได้ **BOM** นำหน้า → sshd อ่าน key ไม่ออก
   ต้องใช้ `-Encoding ascii`

**shell ปลายทางยังเป็น `cmd.exe`** (ตั้ง `DefaultShell` ใน registry แล้วแต่ไม่มีผล) วิธีที่ใช้ได้จริงคือ
ส่งเป็น `powershell -NoProfile -EncodedCommand <base64 ของ UTF-16LE>` เลี่ยงปัญหา quote ทั้งหมด
และ **อย่าใส่ภาษาไทยในสคริปต์ฝั่ง remote** เพราะ encoding เพี้ยนตอนส่งกลับ

`Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` **ค้าง** บนเครื่องนี้
(เครื่องถูก policy ชี้ไป WSUS) สุดท้ายติดตั้งสำเร็จด้วยวิธีอื่น

### ระบบสำรองฐานข้อมูล (ตั้ง 13 ส.ค. 2569)

ก่อนหน้านี้ **ไม่มีระบบสำรองใด ๆ เลย** — ไม่มี scheduled task ไม่มีไฟล์ dump
มีแต่ binlog 6 ไฟล์ซึ่งกู้อะไรไม่ได้ถ้าไม่มี full backup เป็นฐานตั้งต้น

| หัวข้อ | ค่า |
|---|---|
| Scheduled Task | `emoneys-db-backup` — ทุกวัน **02:00** (เครื่อง UTC+07:00 Bangkok) |
| รันในนาม | `SYSTEM` RunLevel Highest — ไม่ต้องมีใคร login |
| สคริปต์ | `C:\backup\backup-emoneys.ps1` (อ่านรหัสจาก `.env` ตอนรัน ไม่ hardcode) |
| ผลลัพธ์ | `C:\backup\emoneys-YYYYMMDD-HHMMSS.zip` — dump 62.6 MB → zip **7.45 MB** |
| log | `C:\backup\backup.log` + `LastTaskResult` ของ Task Scheduler |
| retention | 30 วัน (ลบ `.zip` เก่าอัตโนมัติ) |

ดึงไฟล์ออกนอกเครื่อง (เจ้าของระบบทำเองรายสัปดาห์):

```powershell
scp -i C:\Users\azimuthotg\.ssh\emoneys_prod Administrator@110.78.83.103:"C:/backup/emoneys-20260813-143406.zip" D:\
```

⚠️ **ข้อจำกัดที่ยังเหลือ** — ไฟล์อยู่บนดิสก์ลูกเดียวกับฐานข้อมูล (ดิสก์เสีย = หายทั้งคู่),
**ยังไม่เคยทดสอบ restore จริง**, และไม่มีการแจ้งเตือนเมื่อ backup ล้ม

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
