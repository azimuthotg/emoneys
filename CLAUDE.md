<!-- PROJECT-STATUS
name: emoneys (edoc_system / e-Money receipts)
status: active
deployment: production
deploy_url: http://110.78.83.103/
deploy_server: 110.78.83.103
deploy_os: Windows Server
deploy_method: Waitress (ยืนยันจาก server header) + git pull บนเครื่อง
deploy_path: C:\projects\emoneys (บนเครื่อง prod — ตาม nms_agent/docs/projects/emoneys.md)
deploy_db: MySQL บนเครื่องเดียวกัน
deploy_notes:
  - health check: http://110.78.83.103/health/ (verified โดย nms_agent)
  - HTTP ผ่าน IP ตรง ไม่มี domain/HTTPS
progress: 85
phase: ระบบใช้งานจริงอยู่ — เปิดรอบปรับปรุงใหม่ (ส.ค. 2569) เริ่มจากรื้อเอกสารให้ตรงปัจจุบันแล้ว ต่อด้วยแก้บั๊กเลขที่เอกสาร
next:
  - แก้ race condition ตอนออกเลขที่ใบสำคัญ — atomic block ใน Receipt.generate_receipt_number() ปิดก่อน INSERT จริง
  - แก้การนับ last_document_number ให้กรองด้วยทุก department ที่ใช้ code เดียวกัน (ตอนนี้กรอง department เดียว ไม่ตรงกับตอนออกเลข)
  - เพิ่ม receipt_cancel_approve / receipt_cancel_approve_manager เข้า Permission.PERMISSION_TYPES ให้ตรงกับที่ create_permissions.py สร้างจริง
  - ตั้ง EMAIL_BACKEND เป็น SMTP บน production (ตอนนี้เป็น console อีเมลแจ้งเตือนไม่ออกจริง)
  - ตัดสินใจเรื่อง push notification — ถอด pywebpush ออก หรือเขียนส่วนส่งให้เสร็จ
risks:
  - เลขที่ใบสำคัญซ้ำได้เมื่อมีคนกดเสร็จสิ้นพร้อมกัน (เอกสารการเงิน แก้ย้อนหลังยาก)
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
