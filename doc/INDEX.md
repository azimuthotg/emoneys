# 📋 INDEX.md — ดัชนีเอกสารโครงการ emoneys

> **ระบบบริหารจัดการใบเสร็จ / e-Money — มหาวิทยาลัยนครพนม (NPU)**
> ระบบ Django สำหรับออกใบเสร็จรับเงิน จัดการเล่มเอกสาร (Document Volume) ระบบอนุมัติ
> และจัดการผู้ใช้/สิทธิ์ พร้อมระบบล็อกอินแบบไฟล์/AD

---

## ภาพรวมโครงการ

| หัวข้อ | รายละเอียด |
|---|---|
| ชื่อระบบ | NPU Receipt / e-Money Management System |
| เทคโนโลยี | Django (Python), single app `accounts` |
| Repository | `azimuthotg/emoneys` (branch `main`) |
| เริ่มโครงการ | 9 ตุลาคม 2025 |
| โครงสร้างหลัก | `accounts/` (app), `edoc_system/` (settings/urls), `templates/`, `utils/` |

### Django Models หลัก (`accounts/models.py`)

`User`, `Department`, `Role`, `Permission`, `UserRole`, `FieldLock`,
`DocumentVolume`, `DocumentVolumeLog`, `ReceiptTemplate`, `Receipt`, `ReceiptItem`,
`ReceiptEditRequest`, `ReceiptEditRequestItem`, `ReceiptCancelRequest`,
`UserActivityLog`, `ReceiptChangeLog`, `NPUApiLog`

---

## 📚 เอกสารหลัก

### คู่มือผู้ใช้ / ผู้ดูแลระบบ
| เอกสาร | รายละเอียด |
|---|---|
| `docs/USER_GUIDE_OVERVIEW.md` | ภาพรวมการใช้งานสำหรับผู้ใช้ |
| `docs/admin_management_manual.md` | คู่มือผู้ดูแลระบบ (ฉบับเต็ม) |
| `docs/admin_quick_reference.md` | คู่มืออ้างอิงด่วนสำหรับผู้ดูแล |
| `docs/SUMMARY.md` | สรุปฟีเจอร์ฝั่ง admin |
| `README.md` | คู่มือติดตั้ง / ภาพรวมระบบล็อกอิน |

### เอกสารสถาปัตยกรรม / UML (`docs/`)
| เอกสาร | รายละเอียด |
|---|---|
| `docs/UML_CLASS_DIAGRAM.md` | Class diagram |
| `docs/UML_USE_CASE_DIAGRAM.md` | Use case diagram |
| `docs/UML_SEQUENCE_DIAGRAM.md` | Sequence diagram |
| `docs/UML_ACTIVITY_DIAGRAM.md` | Activity diagram |
| `docs/UML_STATE_DIAGRAM.md` | State diagram |
| `docs/UML_DEPLOYMENT_DIAGRAM.md` | Deployment diagram |

### เอกสารระบบเฉพาะทาง (root)
| เอกสาร | รายละเอียด |
|---|---|
| `CODEBASE_ANALYSIS.md` | วิเคราะห์ codebase |
| `NPU_LOGIN_SYSTEM_GUIDE.md` | คู่มือระบบล็อกอิน NPU |
| `RECEIPT_PDF_GENERATION_GUIDE.md` | การสร้างใบเสร็จ PDF |
| `RECEIPT_PDF_ARCHITECTURE.txt` | สถาปัตยกรรมการออก PDF |
| `notification-system-migration.md` | การย้ายระบบแจ้งเตือน |
| `PYTHON_SCRIPTS_GUIDE.md` | คู่มือสคริปต์ Python (utility) |
| `RESET_RECEIPTS_GUIDE.md` | คู่มือ reset ใบเสร็จ |
| `BASIC_USER_PERMISSION_UPDATE.md` | การปรับสิทธิ์ผู้ใช้พื้นฐาน |

---

## 🚀 Progress Logs (รายวัน)

Progress log รายวันเก็บไว้ในโฟลเดอร์ `doc/` ชื่อ `progress-YYYY-MM-DD.md`
(สร้างอัตโนมัติด้วย `/update-docs done`)

| วันที่ | Progress Log |
|---|---|
| 2026-06-07 | `doc/progress-2026-06-07.md` — เริ่มใช้ระบบเอกสาร, สร้าง INDEX.md |

> หมายเหตุ: log ช่วงต้นโครงการอยู่ที่ root (`PROGRESS_LOG_*.md`, `progress.md`, `PROJECT_PROGRESS.md`)

---

## 🗓️ Timeline การพัฒนา

| วันที่ | สรุปงาน |
|---|---|
| 2025-10-09 | เริ่มโครงการ — ระบบ NPU e-Document & e-Money |
| 2025-10-10 → 10-21 | พัฒนาแกนหลัก: ใบเสร็จ, เล่มเอกสาร, ระบบสิทธิ์/บทบาท, edit request |
| 2025-10-27 → 10-31 | ระบบออก PDF ใบเสร็จ, template, การวาง overlay |
| 2025-11-02 → 11-05 | ระบบ reset ใบเสร็จ, ระบบแจ้งเตือน, volume sharing |
| 2025-11-07 | ปรับปรุงเพิ่มเติม |
| 2026-02-26 → 02-27 | ปรับ login form, password reset (AD/local), key override, pagination, sidebar กระชับ |
| 2026-06-07 | เพิ่ม `/health/` endpoint สำหรับ NMS Agent monitoring; เริ่มใช้ระบบเอกสาร `/update-docs` + สร้าง `doc/INDEX.md` |

---

*อัปเดตล่าสุด: 7 มิถุนายน 2026*
