# 🏛️ File-Based Login System

ระบบล็อกอินแบบไฟล์ที่ดัดแปลงมาจาคคู่มือ NPU Login System เพื่อใช้การยืนยันตัวตนจากไฟล์ CSV แทนการเรียก API ภายนอก

## ✨ คุณสมบัติ

- 🔐 **การยืนยันตัวตนแบบไฟล์** - อ่านข้อมูลผู้ใช้จากไฟล์ CSV
- 👤 **การจัดการผู้ใช้แบบ NPU** - รองรับฟิลด์ข้อมูลผู้ใช้ตามมาตรฐาน NPU
- 🛡️ **ระบบสิทธิ์** - การควบคุมสิทธิ์แบบแยกบทบาท
- ✅ **ระบบอนุมัติ** - การอนุมัติผู้ใช้ใหม่โดยผู้ดูแลระบบ
- 🎨 **UI ภาษาไทย** - อินเทอร์เฟซที่สวยงามและใช้งานง่าย
- 📱 **รองรับมือถือ** - API สำหรับแอปพลิเคชันมือถือ

## 🚀 การติดตั้ง

### 1. Clone โปรเจค
```bash
git clone <repository-url>
cd emoneys
```

### 2. สร้าง Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ
venv\Scripts\activate     # Windows
```

### 3. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 4. สร้างฐานข้อมูล
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. สร้างข้อมูลตัวอย่าง
```bash
python setup_demo.py
```

### 6. เริ่มต้นเซิร์ฟเวอร์
```bash
python manage.py runserver
```

## 🔧 การตั้งค่า

### ไฟล์ผู้ใช้ (data/users.csv)

ระบบจะอ่านข้อมูลผู้ใช้จากไฟล์ `data/users.csv` ที่มีรูปแบบดังนี้:

```csv
ldap_uid,full_name,department,position_title,staff_type,employment_status,contact_email,is_document_staff,can_forward_documents,password_hash
1234567890123,สมชาย ใจดี,สำนักงานอธิการบดี,เจ้าหน้าที่บริหารงานทั่วไป,พนักงานมหาวิทยาลัย,ปฏิบัติงาน,somchai@example.com,true,true,482c811da5d5b4bc6d497ffa98491e38
```

### ฟิลด์ข้อมูล

| ฟิลด์ | คำอธิบาย | ตัวอย่าง |
|-------|----------|----------|
| `ldap_uid` | รหัสบัตรประชาชน (13 หลัก) | `1234567890123` |
| `full_name` | ชื่อ-นามสกุล | `สมชาย ใจดี` |
| `department` | หน่วยงาน | `สำนักงานอธิการบดี` |
| `position_title` | ตำแหน่ง | `เจ้าหน้าที่บริหารงานทั่วไป` |
| `staff_type` | ประเภทบุคลากร | `พนักงานมหาวิทยาลัย` |
| `employment_status` | สถานะการทำงาน | `ปฏิบัติงาน` |
| `contact_email` | อีเมลติดต่อ | `somchai@example.com` |
| `is_document_staff` | เจ้าหน้าที่สารบรรณ | `true/false` |
| `can_forward_documents` | สามารถส่งต่อเอกสาร | `true/false` |
| `password_hash` | รหัสผ่านแฮช (MD5) | `482c811da...` |

### การสร้างรหัสผ่านแฮช

```python
import hashlib
password = "your_password"
password_hash = hashlib.md5(password.encode()).hexdigest()
```

## 👥 บัญชีทดสอบ

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **URL:** http://localhost:8000/admin/

### File-based Accounts
1. **สมชาย ใจดี**
   - **ID:** `1234567890123`
   - **Password:** `password123`
   - สิทธิ์: เจ้าหน้าที่สารบรรณ

2. **สมหญิง รักงาน**
   - **ID:** `9876543210987`
   - **Password:** `mypassword`
   - สิทธิ์: ผู้ใช้ทั่วไป

## 🌐 URL Routes

| URL | คำอธิบาย |
|-----|----------|
| `/` | หน้าล็อกอิน |
| `/login/` | หน้าล็อกอิน |
| `/dashboard/` | หน้าหลักของผู้ใช้ |
| `/profile/` | ข้อมูลส่วนตัว |
| `/admin/` | ระบบจัดการ (Admin) |
| `/logout/` | ออกจากระบบ |
| `/api/login/` | API ล็อกอิน (JSON) |

## 📱 API Usage

### Login API
```javascript
// POST /api/login/
{
    "ldap_uid": "1234567890123",
    "password": "password123"
}

// Response
{
    "success": true,
    "message": "ยินดีต้อนรับ สมชาย ใจดี",
    "user": {
        "id": 1,
        "username": "1234567890123",
        "full_name": "สมชาย ใจดี",
        "department": "สำนักงานอธิการบดี",
        "position_title": "เจ้าหน้าที่บริหารงานทั่วไป",
        "is_document_staff": true,
        "can_forward_documents": true
    }
}
```

## 🔐 ระบบความปลอดภัย

### การยืนยันตัวตน
1. **ตรวจสอบรูปแบบ** - รหัสบัตรประชาชน 13 หลัก
2. **ตรวจสอบรหัสผ่าน** - เปรียบเทียบ MD5 Hash
3. **สถานะการอนุมัติ** - ต้องได้รับการอนุมัติก่อนเข้าใช้งาน
4. **สถานะบัญชี** - ตรวจสอบการระงับการใช้งาน

### Session Management
- **Session Timeout:** 1 ชั่วโมง
- **Secure Cookies:** เปิดใช้ใน Production
- **CSRF Protection:** เปิดใช้งานทั้งระบบ

## 🎛️ การจัดการผู้ใช้

### ผ่าน Django Admin
1. เข้าระบบ Admin: http://localhost:8000/admin/
2. เลือก **Users** เพื่อจัดการผู้ใช้
3. ใช้ Actions เพื่ออนุมัติ/ระงับผู้ใช้แบบกลุ่ม

### การอนุมัติผู้ใช้ใหม่
```python
from accounts.models import User

# อนุมัติผู้ใช้
user = User.objects.get(ldap_uid='1234567890123')
user.approve_user()
```

## 🔧 การปรับแต่ง

### เปลี่ยนที่อยู่ไฟล์ผู้ใช้
```python
# settings.py
USERS_FILE_PATH = '/path/to/your/users.csv'
```

### เปลี่ยนการเข้ารหัสรหัสผ่าน
แก้ไขไฟล์ `accounts/backends.py` ฟังก์ชัน `_verify_password()`

### เพิ่มฟิลด์ข้อมูลผู้ใช้
1. แก้ไข `accounts/models.py`
2. เพิ่มฟิลด์ใน CSV
3. อัปเดต `accounts/backends.py`

## 🚀 Production Deployment

### 1. Environment Variables
```bash
cp .env.example .env
# แก้ไขค่าใน .env
```

### 2. Database
```python
# settings.py - ใช้ MySQL/PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        # ...
    }
}
```

### 3. Static Files
```bash
python manage.py collectstatic
```

### 4. Security Settings
- ตั้งค่า `DEBUG = False`
- กำหนด `ALLOWED_HOSTS`
- ใช้ HTTPS
- ตั้งค่า Security Headers

## 📁 โครงสร้างไฟล์

```
emoneys/
├── accounts/                 # แอปจัดการผู้ใช้
│   ├── models.py            # User model
│   ├── backends.py          # Authentication backend
│   ├── views.py             # Views และ API
│   ├── forms.py             # Django forms
│   └── admin.py             # Admin interface
├── templates/               # Templates
│   ├── base.html           # Base template
│   └── accounts/           # Account templates
├── data/                   # ข้อมูลผู้ใช้
│   └── users.csv           # ไฟล์ผู้ใช้
├── edoc_system/            # Django settings
├── static/                 # Static files
├── manage.py              # Django management
├── setup_demo.py          # สคริปต์สร้างข้อมูลตัวอย่าง
└── requirements.txt       # Dependencies
```

## 🐛 การแก้ไขปัญหา

### ปัญหาการล็อกอิน
1. ตรวจสอบไฟล์ `data/users.csv`
2. ตรวจสอบรหัสผ่านแฮช
3. ตรวจสอบสถานะการอนุมัติ

### ปัญหาการอนุมัติ
```python
# อนุมัติผู้ใช้ผ่าน Shell
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(ldap_uid='1234567890123')
>>> user.approve_user()
```

### ปัญหาฐานข้อมูล
```bash
# รีเซ็ตฐานข้อมูล
rm db.sqlite3
python manage.py migrate
python setup_demo.py
```

## 📚 เอกสารเพิ่มเติม

- [NPU_LOGIN_SYSTEM_GUIDE.md](NPU_LOGIN_SYSTEM_GUIDE.md) - คู่มือต้นฉบับ
- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)

## 🤝 การร่วมพัฒนา

1. Fork โปรเจค
2. สร้าง Feature Branch
3. Commit การเปลี่ยนแปลง
4. Push ไป Branch
5. สร้าง Pull Request

## 📄 License

โปรเจคนี้เป็น Open Source ภายใต้ MIT License

---

**พัฒนาโดย:** Claude Code Assistant  
**วันที่:** 19 กันยายน 2567  
**เวอร์ชัน:** 1.0