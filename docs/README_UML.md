# 📐 UML Documentation - E-Money Voucher System

## 📑 สารบัญเอกสาร UML

เอกสาร UML ทั้งหมดสำหรับระบบออกใบสำคัญรับเงิน แบ่งออกเป็น 6 ประเภทหลัก:

---

## 📚 เอกสาร UML ทั้งหมด

### 1. [**Class Diagram**](./UML_CLASS_DIAGRAM.md) 📦
แสดงโครงสร้างคลาสและความสัมพันธ์ระหว่างคลาส

**เนื้อหา:**
- Core Models (User, Permission, Role, UserRole)
- Receipt System (Receipt, ReceiptItem, ReceiptTemplate)
- Request System (EditRequest, CancelRequest)
- Audit System (ChangeLog, ActivityLog)
- Role & Permission Matrix
- Department Scope Diagram

**เหมาะสำหรับ:**
- นักพัฒนาที่ต้องการเข้าใจโครงสร้างฐานข้อมูล
- การออกแบบ Models ใหม่
- การทำความเข้าใจ Relationships

---

### 2. [**Sequence Diagram**](./UML_SEQUENCE_DIAGRAM.md) 🔄
แสดง Flow การทำงานแบบ Step-by-step

**เนื้อหา:**
- Edit Request Flow (Basic User → Dept Manager)
- Edit Request Flow (Dept Manager → Senior Manager)
- Cancel Request Flow (Basic User)
- Cancel Request Flow (Dept Manager Direct)
- Receipt Creation Flow
- Permission Check Flow
- Department Scope Validation

**เหมาะสำหรับ:**
- เข้าใจ Workflow ของระบบ
- Debug การทำงานที่ผิดพลาด
- วางแผน Feature ใหม่

---

### 3. [**State Diagram**](./UML_STATE_DIAGRAM.md) 🔀
แสดง State และ Transition ของข้อมูล

**เนื้อหา:**
- Receipt Lifecycle (Draft → Completed → Cancelled)
- Edit Request States (Pending → Approved → Applied)
- Cancel Request States
- User Approval States
- Permission Check State Machine
- Document Volume Lifecycle
- Complete System State Flow

**เหมาะสำหรับ:**
- เข้าใจ Status ต่างๆ
- วางแผน State Management
- ทดสอบ Edge Cases

---

### 4. [**Use Case Diagram**](./UML_USE_CASE_DIAGRAM.md) 👥
แสดงการใช้งานของแต่ละ Actor

**เนื้อหา:**
- Overall System Use Cases
- Basic User Use Cases
- Department Manager Use Cases
- Senior Manager Use Cases
- System Admin Use Cases
- Public User Use Cases (QR Verification)
- Complete Workflow Diagram

**เหมาะสำหรับ:**
- Business Analyst
- Product Owner
- การทำ User Stories
- การวางแผน Features

---

### 5. [**Activity Diagram**](./UML_ACTIVITY_DIAGRAM.md) 🎯
แสดง Activities และ Decision Points

**เนื้อหา:**
- Receipt Creation Activity
- Edit Request Submission & Approval
- Cancel Request Activity
- Permission Check Activity
- Department Scope Validation
- User Registration & Approval
- Report Generation Activity
- Audit Logging Activity

**เหมาะสำหรับ:**
- เข้าใจ Business Process
- วางแผน Automation
- Optimize Workflow
- ทำ Process Documentation

---

### 6. [**Deployment Diagram**](./UML_DEPLOYMENT_DIAGRAM.md) 🏗️
แสดงสถาปัตยกรรมและการ Deploy

**เนื้อหา:**
- System Deployment Architecture
- Component Architecture
- Receipt System Components
- Permission System Components
- Network Topology (Production)
- Database Schema Components
- CI/CD Pipeline

**เหมาะสำหรับ:**
- DevOps Engineers
- System Architects
- การวางแผน Infrastructure
- Production Deployment

---

## 🎯 การใช้งาน UML Diagrams

### สำหรับนักพัฒนา (Developers):
1. **เริ่มต้น:** อ่าน [Class Diagram](./UML_CLASS_DIAGRAM.md) เพื่อเข้าใจโครงสร้าง
2. **ทำความเข้าใจ Flow:** อ่าน [Sequence Diagram](./UML_SEQUENCE_DIAGRAM.md)
3. **ดู State Management:** อ่าน [State Diagram](./UML_STATE_DIAGRAM.md)
4. **เข้าใจ Architecture:** อ่าน [Deployment Diagram](./UML_DEPLOYMENT_DIAGRAM.md)

### สำหรับ Business Analyst / Product Owner:
1. **เริ่มต้น:** อ่าน [Use Case Diagram](./UML_USE_CASE_DIAGRAM.md)
2. **ทำความเข้าใจ Process:** อ่าน [Activity Diagram](./UML_ACTIVITY_DIAGRAM.md)
3. **ดู Workflow:** อ่าน [Sequence Diagram](./UML_SEQUENCE_DIAGRAM.md)

### สำหรับ Testers / QA:
1. **ทำความเข้าใจ Flow:** อ่าน [Sequence Diagram](./UML_SEQUENCE_DIAGRAM.md)
2. **Test Cases:** ใช้ [Use Case Diagram](./UML_USE_CASE_DIAGRAM.md)
3. **State Testing:** ใช้ [State Diagram](./UML_STATE_DIAGRAM.md)
4. **Process Testing:** ใช้ [Activity Diagram](./UML_ACTIVITY_DIAGRAM.md)

### สำหรับ DevOps / System Admin:
1. **Infrastructure:** อ่าน [Deployment Diagram](./UML_DEPLOYMENT_DIAGRAM.md)
2. **ทำความเข้าใจ Components:** ดู Component Architecture
3. **Database:** ดู Database Schema Components

---

## 🔑 Key Concepts ที่ต้องเข้าใจ

### 1. **Role Hierarchy** (ลำดับชั้นของบทบาท)
```
System Admin (ทั้งระบบ)
    ↓
Senior Manager (ระดับแผนก - อนุมัติ Dept Manager)
    ↓
Department Manager (ระดับแผนก - อนุมัติ Basic User)
    ↓
Basic User (ผู้ใช้ทั่วไป - ส่งคำขอ)
```

### 2. **Approval Flow** (การอนุมัติ)
```
Basic User Request
    → Department Manager Approves

Department Manager Request
    → Senior Manager Approves

Senior Manager Request
    → Another Senior Manager / Admin Approves
```

### 3. **Department Scope** (ขอบเขตแผนก)
- ผู้อนุมัติต้องอยู่**แผนกเดียวกัน**กับผู้ส่งคำขอ
- ยกเว้น: System Admin สามารถเข้าถึงทุกแผนก

### 4. **Permission Types** (ประเภทสิทธิ์)
```
receipt_create              - สร้างใบสำคัญ
receipt_view_own           - ดูของตัวเอง
receipt_view_department    - ดูแผนกตัวเอง
receipt_view_all          - ดูทั้งหมด

receipt_edit_approve       - อนุมัติ Basic User
receipt_edit_approve_manager - อนุมัติ Dept Manager

receipt_cancel_approve     - อนุมัติยกเลิก Basic User
receipt_cancel_approve_manager - อนุมัติยกเลิก Dept Manager
receipt_cancel_department  - ยกเลิกโดยตรง
```

### 5. **Receipt States** (สถานะใบสำคัญ)
```
Draft → Completed → Cancelled
  ↓         ↓
  Edit    Edit Request → Approved → Applied
  (Direct)
```

---

## 🛠️ การใช้งาน PlantUML

### ติดตั้ง PlantUML:

**Option 1: VS Code Extension**
```bash
# ติดตั้ง Extension
- ชื่อ: PlantUML
- Publisher: jebbs
```

**Option 2: Online**
- เว็บไซต์: https://www.plantuml.com/plantuml/uml/

**Option 3: Command Line**
```bash
# ติดตั้ง PlantUML
brew install plantuml  # macOS
sudo apt-get install plantuml  # Ubuntu

# สร้างรูปภาพ
plantuml diagram.puml
```

### การ Render Diagrams:

1. **ใน VS Code:**
   - เปิดไฟล์ `.md`
   - กด `Alt + D` เพื่อ Preview

2. **Export เป็นรูปภาพ:**
   ```bash
   plantuml -tpng UML_CLASS_DIAGRAM.md
   plantuml -tsvg UML_SEQUENCE_DIAGRAM.md
   ```

3. **Online:**
   - Copy โค้ด PlantUML
   - Paste ที่ https://www.plantuml.com/plantuml/uml/

---

## 📊 สรุประบบ

### **ระบบประกอบด้วย:**

**1. User Management**
- 4 Roles (Admin, Senior Manager, Dept Manager, Basic User)
- 20+ Permissions
- Department-based Access Control

**2. Receipt Management**
- Create/Edit/Cancel Receipts
- Draft and Completed states
- PDF Generation with QR Code

**3. Request Management**
- Edit Request (with approval)
- Cancel Request (with approval)
- Multi-level approval workflow

**4. Audit & Logging**
- Complete audit trail
- User activity logging
- Change history

**5. Reports & Analytics**
- Department reports
- Revenue summary
- Activity statistics

---

## 🔍 ตัวอย่างการใช้งาน

### ตัวอย่าง 1: Basic User สร้างใบสำคัญและขอแก้ไข

```
1. Basic User สร้างใบสำคัญ (Completed)
   → ใช้ [Activity Diagram - Receipt Creation]

2. ต้องการแก้ไข
   → ส่งคำขอแก้ไข
   → ใช้ [Sequence Diagram - Edit Request Basic User]

3. Dept Manager อนุมัติ
   → ตรวจสอบ Permission
   → ใช้ [State Diagram - Edit Request States]

4. ระบบ Apply การเปลี่ยนแปลง
   → Log Audit Trail
   → ใช้ [Activity Diagram - Audit Logging]
```

### ตัวอย่าง 2: Dept Manager ยกเลิกใบสำคัญ

```
1. Dept Manager เลือกใบสำคัญ
   → ตรวจสอบสิทธิ์
   → ใช้ [Use Case Diagram - Dept Manager]

2. ยกเลิกโดยตรง (Direct Cancel)
   → ใช้ [Sequence Diagram - Direct Cancel]

3. ระบบบันทึก
   → Change status to Cancelled
   → Create audit log
   → ใช้ [State Diagram - Receipt Lifecycle]
```

---

## 📞 การใช้งานเพิ่มเติม

### สร้าง Diagram ใหม่:
1. สร้างไฟล์ `.md` หรือ `.puml`
2. เริ่มต้นด้วย:
   ```plantuml
   @startuml
   !theme plain
   title Your Diagram Title

   ' Your diagram code here

   @enduml
   ```
3. ใช้ Syntax จาก PlantUML: https://plantuml.com/

### Update Diagram:
1. แก้ไขโค้ด PlantUML
2. Re-render ผ่าน VS Code หรือ Online
3. Export รูปภาพถ้าต้องการ

---

## 📝 Changelog

### Version 1.0 (2 ตุลาคม 2568)
- ✅ สร้าง Class Diagram
- ✅ สร้าง Sequence Diagram (7 scenarios)
- ✅ สร้าง State Diagram (7 states)
- ✅ สร้าง Use Case Diagram (6 actors)
- ✅ สร้าง Activity Diagram (8 activities)
- ✅ สร้าง Deployment Diagram (7 diagrams)
- ✅ สร้าง README สำหรับ UML

---

**พัฒนาโดย:** Claude Code Assistant
**วันที่:** 2 ตุลาคม 2568
**Status:** ✅ Complete
