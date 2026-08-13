<!-- PROJECT-STATUS
name: emoneys (edoc_system / e-Money receipts)
status: active
deployment: production
deploy_url: http://110.78.83.103/
deploy_server: 110.78.83.103
deploy_os: Windows Server
deploy_method: NSSM (C:\nssm\win64\nssm.exe) ห่อเป็น Windows Service ชื่อ emoneys (Automatic, LocalSystem) สั่ง C:\emoneys\emoney_env\Scripts\python.exe -m waitress --listen=0.0.0.0:80 edoc_system.wsgi:application + git pull บนเครื่อง
deploy_path: C:\emoneys (ตรวจบนเครื่องจริง 2026-08-13 — เอกสารเก่าที่ระบุ C:\projects\emoneys หรือ C:\inetpub\wwwroot\emoneys ผิดทั้งคู่)
deploy_db: MySQL ฐาน emoneys บนเครื่องเดียวกัน แต่ต่อผ่าน public IP 110.78.83.103 ไม่ใช่ localhost
deploy_notes:
  - health check: http://110.78.83.103/health/ (verified 2026-08-13 — 200, db ok)
  - HTTP ผ่าน IP ตรง ไม่มี domain/HTTPS/reverse proxy
  - reboot แล้วขึ้นเอง เพราะเป็น Windows Service แบบ Automatic
  - prod รัน DEBUG=True และ static ถูกเสิร์ฟผ่านบล็อก if settings.DEBUG ใน urls.py — สลับเป็น False เฉย ๆ จะทำเว็บล่ม ดู MEM.md
  - ข้อมูลจริง ณ 2026-08-13: ใบสำคัญ completed 10,484 ใบ, 25 หน่วยงาน, ไม่มีเลขซ้ำเลย
progress: 85
phase: รื้อเอกสารให้ตรงกับระบบจริงเสร็จแล้ว (13 ส.ค. 2569) — คิวแก้บั๊กรอเจ้าของว่างมาลงมือต่อ ระบบยังใช้งานจริงตามปกติ
next:
  - แก้ DEBUG=True บน prod แบบปลอดภัย — กู้ pip ใน venv ก่อน (ensurepip) แล้วติดตั้ง whitenoise แยก SECURE_SSL_REDIRECT ออกจาก DEBUG ค่อยปิด DEBUG (ปิดเฉย ๆ เว็บล่มทันที ดู MEM.md)
  - เปลี่ยน service emoneys จาก LocalSystem เป็น service account ที่มีสิทธิ์เท่าที่จำเป็น
  - แก้ race condition ตอนออกเลขที่ใบสำคัญ — ย้ายตัวนับไปบนแถว DocumentVolume + select_for_update แถวนั้น + ขยาย atomic ให้ครอบ INSERT
  - เพิ่มการดัก IntegrityError ใน receipt_complete_draft_ajax (ตอนนี้ receipt.save() เปล่า ๆ ชนแล้วได้ 500)
  - แก้การนับ last_document_number ให้กรองด้วยทุก department ที่ใช้ code เดียวกัน (ตอนนี้กรอง department เดียว ไม่ตรงกับตอนออกเลข)
  - เพิ่ม receipt_cancel_approve / receipt_cancel_approve_manager เข้า Permission.PERMISSION_TYPES ให้ตรงกับที่ create_permissions.py สร้างจริง
  - ตั้ง EMAIL_BACKEND เป็น SMTP บน production (ตอนนี้เป็น console อีเมลแจ้งเตือนไม่ออกจริง)
  - ตัดสินใจเรื่อง push notification — ถอด pywebpush ออก หรือเขียนส่วนส่งให้เสร็จ
  - ถามเจ้าของว่า GitHub PAT ที่เคยหลุดถูก revoke แล้วหรือยัง (remote สะอาดทั้ง dev และ prod แล้วแต่ไม่ได้แปลว่า token ตาย)
risks:
  - prod รัน DEBUG=True — หน้า error 500 โชว์ SECRET_KEY รหัส MySQL และ NPU token บนเว็บที่เปิด HTTP สาธารณะ
  - MySQL ผูกกับ public IP 110.78.83.103 ไม่ใช่ localhost
  - service รันด้วยสิทธิ์ LocalSystem สูงเกินความจำเป็น
  - เลขที่ใบสำคัญซ้ำได้ทางทฤษฎีเฉพาะหน่วยงานคนละ row ที่ใช้ code เดียวกัน (จริงยังไม่เคยเกิดใน 10,484 ใบ)
  - NPU API token อายุ 365 วัน ไม่มี auto-refresh ถ้าลืมต่อ ระบบล็อกอินตายทั้งระบบ
updated: 2026-08-13
-->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ระบบใบสำคัญรับเงินอิเล็กทรอนิกส์ (e-Money / edoc_system) ของ **มหาวิทยาลัยนครพนม (NPU)**
Django 4.2 + MySQL แอปเดียวชื่อ `accounts` — ล็อกอินผ่าน NPU API (บุคลากร/นักศึกษา)
ออกเลขที่เอกสารตามปีงบประมาณไทย สร้าง PDF พร้อม QR code ตรวจสอบสาธารณะ
และมี workflow ขอแก้ไข/ขอยกเลิกใบสำคัญ

**อ่าน 3 ไฟล์นี้ก่อนเริ่มงาน:**

| ไฟล์ | มีอะไร |
|---|---|
| `README.md` | stack, โครงสร้าง, แนวคิดหลัก 4 เรื่อง (เลขที่เอกสาร / เล่ม / สิทธิ์ / auth) |
| `MEM.md` | ปัญหา & วิธีแก้, การตัดสินใจเชิงออกแบบ, หมายเหตุ — สะสมรายวัน |
| `doc/INDEX.md` | ดัชนีเอกสาร + progress log รายวัน (`doc/progress-YYYY-MM-DD.md`) |

`docs/` เก็บคู่มือผู้ดูแลระบบและ UML diagrams (ต.ค. 2568 — เนื้อหาระดับ workflow ยังใช้ได้)

## ⛔ อย่าอ่าน `_archive/`

เอกสารวิเคราะห์เก่า, progress log เก่า และสคริปต์รันครั้งเดียว ถูกย้ายไป `_archive/`
(อยู่ใน `.gitignore` แล้ว) เมื่อ 13 ส.ค. 2569 เพราะ **เนื้อหาผิดและทำให้หลงทาง** —
ระบุชื่อมหาวิทยาลัยผิด บอกว่าใช้ SQLite อ้างเลขบรรทัดที่เลื่อนไปแล้ว และอธิบายไฟล์ที่ไม่มีอยู่จริง
ห้ามใช้เป็นแหล่งอ้างอิงหรือคัดลอกข้อมูลออกมา

`tools/` เก็บสคริปต์ซ่อมบำรุงที่ยังใช้ได้ 3 ตัว — ไม่ใช่ส่วนของแอป ดู `tools/README.md`

## Known Issues / Notes

- Auth ใช้ NPU API เดียวกันสำหรับทั้งบุคลากรและนักศึกษา — **token เดียว** (`NPU_API_TOKEN`)
  `NPU_STUDENT_API_TOKEN` ใน settings ชี้มาที่ตัวเดียวกัน ไม่ต้องตั้งแยก
- Token อายุ 365 วัน ต้องต่อมือทุกปี ไม่มี auto-refresh
- ฐานข้อมูลคือ **MySQL เท่านั้น** ไม่มี fallback เป็น SQLite (`db.sqlite3` ที่เคยมีคือไฟล์เปล่า ย้ายออกแล้ว)
- `data/users.csv` + `_authenticate_with_file()` ใน backends.py เป็นซากระบบ login แบบไฟล์เดิม
  ไม่มีเส้นทางไหนเรียกถึงแล้ว
- Remote git URL เคยฝัง PAT ไว้ — **ตรวจเมื่อ 13 ส.ค. 2569 แล้วว่าสะอาดแล้ว** (`https://github.com/azimuthotg/emoneys.git`)

## กติกาการปิด session
ก่อนจบงานทุกครั้ง ให้อัปเดตบล็อก <!-- PROJECT-STATUS --> ด้านบนของไฟล์นี้:
ปรับ progress, phase, รายการ next ให้ตรงกับงานจริง และแก้ updated เป็นวันที่ปัจจุบัน
บันทึกปัญหา/วิธีแก้/การตัดสินใจที่เกิดในเซสชันลง `MEM.md`
จากนั้นรัน `python C:\projects\project_status.py` เพื่ออัปเดต dashboard รวม
