# 📋 INDEX.md — ดัชนีเอกสารโครงการ emoneys

> **ระบบใบสำคัญรับเงินอิเล็กทรอนิกส์ / e-Money — มหาวิทยาลัยนครพนม (NPU)**
> Django + MySQL สำหรับออกใบสำคัญรับเงิน จัดการเล่มเอกสารตามปีงบประมาณ
> workflow ขอแก้ไข/ยกเลิก และจัดการผู้ใช้/สิทธิ์ ล็อกอินผ่าน NPU API

---

## ภาพรวมโครงการ

| หัวข้อ | รายละเอียด |
|---|---|
| ชื่อระบบ | NPU Receipt / e-Money Management System (`edoc_system`) |
| เทคโนโลยี | Django 4.2 + MySQL, single app `accounts` |
| Repository | `azimuthotg/emoneys` (branch `main`) |
| เริ่มโครงการ | 9 ตุลาคม 2025 |
| สถานะ | ใช้งานจริงบน production — อยู่ระหว่างรอบปรับปรุง (ส.ค. 2569) |
| โครงสร้างหลัก | `accounts/` (app), `edoc_system/` (settings/urls), `templates/`, `utils/`, `tools/` |

### Django Models หลัก (`accounts/models.py`)

`User`, `Department`, `Role`, `Permission`, `UserRole`, `FieldLock`,
`DocumentVolume`, `DocumentVolumeLog`, `ReceiptTemplate`, `Receipt`, `ReceiptItem`,
`ReceiptEditRequest`, `ReceiptEditRequestItem`, `ReceiptCancelRequest`,
`UserActivityLog`, `ReceiptChangeLog`, `NPUApiLog`

---

## 📚 เอกสารหลัก

### เริ่มที่นี่ (3 ไฟล์นี้คือแหล่งอ้างอิงจริง)

| เอกสาร | รายละเอียด |
|---|---|
| `README.md` | stack, โครงสร้างโปรเจกต์, การติดตั้ง, แนวคิดหลัก 4 เรื่อง (เลขที่เอกสาร / เล่ม / สิทธิ์ / auth) |
| `MEM.md` | ปัญหา & วิธีแก้, บั๊กที่รู้แล้ว, การตัดสินใจเชิงออกแบบ, หมายเหตุ |
| `CLAUDE.md` | บล็อก PROJECT-STATUS (สถานะ + งานที่ต้องทำ) และกติกาการทำงาน |

### คู่มือผู้ใช้ / ผู้ดูแลระบบ (`docs/` — ต.ค. 2568)

| เอกสาร | รายละเอียด |
|---|---|
| `docs/USER_GUIDE_OVERVIEW.md` | ภาพรวมการใช้งานสำหรับผู้ใช้ |
| `docs/admin_management_manual.md` | คู่มือผู้ดูแลระบบ (ฉบับเต็ม) |
| `docs/admin_quick_reference.md` | คู่มืออ้างอิงด่วนสำหรับผู้ดูแล |
| `docs/SUMMARY.md` | สรุปฟีเจอร์ฝั่ง admin |

> เนื้อหาระดับ workflow/หน้าจอ ยังใช้ได้ แต่ไม่ได้อัปเดตตั้งแต่ ต.ค. 2568
> ถ้าขัดกับโค้ด ให้ยึดโค้ดและ `README.md`

### สถาปัตยกรรม / UML (`docs/`)

`UML_CLASS_DIAGRAM.md` · `UML_USE_CASE_DIAGRAM.md` · `UML_SEQUENCE_DIAGRAM.md` ·
`UML_ACTIVITY_DIAGRAM.md` · `UML_STATE_DIAGRAM.md` · `UML_DEPLOYMENT_DIAGRAM.md`

### ⛔ `_archive/` — ห้ามใช้อ้างอิง

เอกสารวิเคราะห์เก่า, progress log เก่า และสคริปต์รันครั้งเดียว ถูกย้ายออกเมื่อ 13 ส.ค. 2569
เพราะเนื้อหาผิด (ชื่อมหาวิทยาลัยผิด, บอกว่าใช้ SQLite, อ้างเลขบรรทัดที่เลื่อนแล้ว,
อธิบายไฟล์ที่ไม่มีจริง) โฟลเดอร์อยู่ใน `.gitignore` — รายละเอียดที่ `_archive/README.md`

---

## 🚀 Progress Logs (รายวัน)

เก็บใน `doc/progress-YYYY-MM-DD.md`

| วันที่ | Progress Log |
|---|---|
| 2026-06-07 | `doc/progress-2026-06-07.md` — เริ่มใช้ระบบเอกสาร, สร้าง INDEX.md |
| 2026-08-13 | `doc/progress-2026-08-13.md` — รื้อเอกสารทั้งโปรเจกต์, สร้าง MEM.md, เปิดสถานะ active |

---

## 🗓️ Timeline การพัฒนา

| วันที่ | สรุปงาน |
|---|---|
| 2025-10-09 | เริ่มโครงการ — ระบบ NPU e-Document & e-Money |
| 2025-10-10 → 10-21 | พัฒนาแกนหลัก: ใบสำคัญ, เล่มเอกสาร, ระบบสิทธิ์/บทบาท, edit request |
| 2025-10-27 → 10-31 | ระบบออก PDF, template, การวาง overlay |
| 2025-11-02 → 11-05 | ระบบ reset ใบสำคัญ, ระบบแจ้งเตือน, volume sharing, จำกัดสิทธิ์ Basic User |
| 2026-02-26 → 02-27 | ปรับ login form, password reset (AD/local), key override, pagination, sidebar กระชับ |
| 2026-06-07 | เพิ่ม `/health/` endpoint สำหรับ NMS Agent monitoring; เริ่มใช้ระบบเอกสาร `doc/` |
| 2026-06-20 | รวม NPU API token เหลือตัวเดียว — แก้ปัญหานักศึกษาล็อกอินไม่ได้ (commit `c08b6dc`) |
| 2026-08-13 | รื้อเอกสารให้ตรงกับระบบจริง ย้ายของเก่าเข้า `_archive/` เปิดรอบปรับปรุงใหม่ |

---

*อัปเดตล่าสุด: 13 สิงหาคม 2569*
