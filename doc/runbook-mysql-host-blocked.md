# Runbook — MySQL บล็อก host (`ERROR 1129`) ต่อจากข้างนอกไม่ได้

> สร้าง 13 ส.ค. 2569 จากการวิเคราะห์เหตุจริงบนเครื่อง prod `110.78.83.103`
> ใช้เมื่อ DBeaver/ไคลเอนต์จากนอกเครื่องขึ้นข้อความ
> `Host '110.78.83.1' is blocked because of many connection errors`

---

## สรุปกลไกที่ทำให้เกิด

1. ทุก connection ที่มาจากนอกเครื่องถูก NAT ยุบเป็น IP เดียวคือ `110.78.83.1`
   (gateway ของ subnet `110.78.83.0/25`) — ยืนยันจาก `performance_schema.host_cache`
   ที่มีแค่ 2 แถวคือ NAT ตัวนี้ กับตัวเครื่องเอง
2. MySQL นับ **handshake error** สะสมต่อ IP เมื่อถึง `max_connect_errors` จะบล็อก IP นั้น
3. `max_connect_errors` เป็นค่า default = **100** ซึ่งต่ำเกินไป
4. พอ `110.78.83.1` โดนบล็อก = **ทุกคนที่อยู่นอกเครื่องโดนพร้อมกันหมด**

**แอปบนเครื่อง prod ไม่ได้รับผลกระทบ** เพราะต่อ DB จาก `110.78.83.103 → 110.78.83.103`
วนในเครื่อง ไม่ผ่าน NAT (NIC ถือ public IP ตัวนี้โดยตรง)

`AUTHENTICATION_ERRORS` **ไม่นับ**เข้าโควตาบล็อก — รหัสผ่านผิดไม่ทำให้โดนบล็อก

---

## หลักฐานที่เก็บได้ ณ 13 ส.ค. 2569

```
IP: 110.78.83.1        HOST: NULL       HOST_VALIDATED: YES
SUM_CONNECT_ERRORS         : 101    <-- เกิน max_connect_errors (100)
COUNT_HANDSHAKE_ERRORS     : 101    <-- ต้นเหตุ 100%
COUNT_NAMEINFO_TRANSIENT   : 0
COUNT_NAMEINFO_PERMANENT   : 1      <-- DNS ไม่ใช่สาเหตุ
COUNT_AUTHENTICATION_ERRORS: 104    <-- ไม่นับเข้าโควตา
COUNT_HOST_BLOCKED_ERRORS  : 2735   <-- ถูกปฏิเสธหลังบล็อกแล้ว
FIRST_SEEN: 2026-08-01 02:52:56   LAST_ERROR_SEEN: 2026-08-13 13:33:40

IP: 110.78.83.103      HOST: WIN-4CJMG6HCBQJ
SUM_CONNECT_ERRORS: 0   COUNT_AUTHENTICATION_ERRORS: 4
```

ค่าอื่นที่เกี่ยวข้อง: `max_connect_errors=100`, `skip_name_resolve=OFF`,
`bind_address=*`, `host_cache_size=279`, MySQL `8.0.44`,
`Aborted_connects=2924` จาก `Connections=22378` ใน uptime 13.1 วัน

ประวัติการโดนบล็อก (จาก error log — เห็นเฉพาะที่ผ่าน plugin `mysqlx` port 33060):
**4 มิ.ย. / 17 มิ.ย. / 20 ก.ค. / 7 ส.ค. 2569** — การบล็อกบน port 3306 ปกติ **ไม่ถูกเขียนลง log**

---

## ขั้นตอนปลดบล็อก

รันบนเครื่อง prod (RDP หรือ SSH) — ต้องใช้สิทธิ์ `RELOAD` จึงต้องเป็น root

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -e "FLUSH HOSTS;"
```

MySQL 8.0.23+ ถือว่า `FLUSH HOSTS` deprecated (ยังใช้ได้ แต่จะเตือน) ตัวเทียบเท่ารุ่นใหม่:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -e "TRUNCATE TABLE performance_schema.host_cache;"
```

**ก่อนรัน** ถ้ายังไม่ได้เก็บหลักฐาน ให้ query `host_cache` ไว้ก่อน เพราะคำสั่งนี้ล้างตารางทิ้ง

---

## ประเมินความเสี่ยง

| ประเด็น | ผล |
|---|---|
| แตะข้อมูลในฐาน (แถว/ตาราง/schema) | **ไม่** — ล้าง cache ในหน่วยความจำเท่านั้น |
| เขียนไฟล์ลงดิสก์ | **ไม่** |
| ตัด connection ที่เปิดอยู่ | **ไม่** — session ที่ทำงานอยู่ไม่กระทบ |
| ต้อง restart MySQL | **ไม่** |
| เว็บ/แอปล่ม | **ไม่** — แอปต่อ DB คนละเส้นทาง ไม่ได้โดนบล็อกอยู่แล้ว |
| ผลข้างเคียงที่มีจริง | ตัวนับใน `host_cache` หายหมด = เสียหลักฐานการวิเคราะห์ |

**ระดับความเสี่ยง: ต่ำมาก** เป็นการคืนสถานะให้กลับไปเหมือนก่อน 7 ส.ค.
ไม่ได้เปิดสิทธิ์อะไรใหม่ ไม่ได้ผ่อนการตั้งค่าความปลอดภัยใด ๆ

### เรื่อง backup

**การปลดบล็อกไม่ต้อง backup** เพราะไม่มีอะไรให้เสียหาย — ไม่แตะข้อมูลเลยแม้แต่แถวเดียว

แต่ตรวจเมื่อ 13 ส.ค. 2569 พบว่า **เครื่องนี้ไม่มีระบบสำรองฐานข้อมูลใด ๆ ทั้งสิ้น**
ไม่มี scheduled task, ไม่มีไฟล์ dump บนดิสก์ มีแต่ binlog 6 ไฟล์ (21 ก.ค.–ปัจจุบัน, 180 MB)
ซึ่ง **กู้อะไรไม่ได้ถ้าไม่มี full backup เป็นฐาน** — นี่คือความเสี่ยงที่ใหญ่กว่าเรื่องบล็อกมาก
(datadir แค่ 553 MB, ดิสก์ว่าง 73 GB — ทำ backup ได้สบาย)

> ✅ **แก้แล้ว 13 ส.ค. 2569** — ดูหัวข้อ "ระบบสำรองข้อมูล" ด้านล่าง

---

## แผนย้อนกลับ (rollback)

`FLUSH HOSTS` **ไม่มีอะไรต้องย้อนกลับ** ไม่ได้เปลี่ยน config ไม่ได้เขียนไฟล์
ถ้าอยากได้สถานะเดิมคือ "โดนบล็อก" กลับมา ก็แค่รอให้ error สะสมใหม่ (ดูหัวข้อถัดไป)

ถ้าเกิดอาการผิดปกติหลังรัน ให้เก็บข้อมูลชุดนี้เพื่อวินิจฉัย — ไม่ต้อง restart อะไร:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -e "SELECT * FROM performance_schema.host_cache\G SHOW GLOBAL STATUS LIKE 'Aborted%'; SHOW PROCESSLIST;"
```

### ถ้าภายหลังทำขั้น "กันไม่ให้เกิดซ้ำ" ด้วย `SET PERSIST`

คำสั่งที่จะใช้คือ `SET PERSIST max_connect_errors = 1000000;`
ซึ่งเขียนลงไฟล์ `C:\ProgramData\MySQL\MySQL Server 8.0\Data\mysqld-auto.cnf`
(ตรวจแล้วว่า **ยังไม่เคยมีไฟล์นี้** = ยังไม่เคยมีใครใช้ `SET PERSIST` บนเครื่องนี้)

ย้อนกลับได้ 2 ทาง:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -e "RESET PERSIST max_connect_errors; SET GLOBAL max_connect_errors = 100;"
```

หรือถ้า MySQL start ไม่ขึ้นเพราะไฟล์นี้เสีย: หยุด service `MySQL80` → ลบ/เปลี่ยนชื่อ
`mysqld-auto.cnf` → start ใหม่ (กลับไปใช้ค่าจาก `my.ini` ล้วน)

**ข้อแลกเปลี่ยนที่ต้องรู้** — ตั้งค่าสูงขนาดนั้นเท่ากับปิดกลไก auto-block ทิ้ง
กลไกนี้กัน brute-force รหัสผ่าน **ไม่ได้อยู่แล้ว** (auth error ไม่ถูกนับ) และในโครงสร้าง
NAT แบบนี้มันกลายเป็นการ DoS ตัวเอง จึงเป็นการแลกที่คุ้ม แต่ของจริงที่ควรกันคือ
จำกัดการเข้าถึง port 3306/33060 ที่ระดับเครือข่าย

---

## พยากรณ์การเกิดซ้ำ

ถ้า `FLUSH HOSTS` อย่างเดียวโดยไม่แตะ `max_connect_errors`:
สถิติจริงคือสะสม ~100 handshake error ในช่วง **1–7 ส.ค. = ~17 ครั้ง/วัน**
→ คาดว่าจะกลับมาโดนบล็อกอีกใน **ประมาณ 6 วัน**

---

## งานที่ยังค้าง (ยังไม่ได้ทำ ณ 13 ส.ค. 2569)

1. หาว่าอะไรยิง connection เข้ามา **~456 ครั้ง/วัน** จากนอกเครื่อง
   (`COUNT_HOST_BLOCKED_ERRORS` 2735 ใน 6 วัน) — อาจมีระบบอื่นที่พังอยู่โดยไม่มีใครรู้
2. ตั้ง `max_connect_errors` ให้สูงขึ้น (ดูหัวข้อ rollback ประกอบ)
3. `skip_name_resolve=ON` — ต้องแก้ `my.ini` + restart MySQL
   **ต้องเช็ก `SELECT user, host FROM mysql.user;` ก่อน** ถ้ามี user ผูกกับชื่อโฮสต์จะล็อกอินไม่ได้ทันที
4. จำกัดการเข้าถึง 3306 / 33060 ที่ firewall — และพิจารณาปิด plugin `mysqlx` ถ้าไม่ได้ใช้
5. `emoneys@%` มี `ALL PRIVILEGES` ต่อได้จากทุกที่ รหัสผ่าน 12 ตัว auth ด้วย
   `mysql_native_password` ที่ deprecated แล้ว
6. ~~ตั้งระบบ backup ฐานข้อมูล~~ ✅ ทำแล้ว 13 ส.ค. 2569 (ดูด้านล่าง)
   — เหลือ **ทดสอบกู้คืนจริง** ซึ่งยังไม่ได้ทำ

---

## ระบบสำรองข้อมูล (ตั้งเมื่อ 13 ส.ค. 2569)

| หัวข้อ | ค่า |
|---|---|
| Scheduled Task | `emoneys-db-backup` — รันทุกวัน **02:00** (เครื่องเป็น UTC+07:00 Bangkok) |
| รันในนาม | `SYSTEM` (RunLevel Highest) — ทำงานแม้ไม่มีใคร login |
| สคริปต์ | `C:\backup\backup-emoneys.ps1` |
| ปลายทาง | `C:\backup\emoneys-YYYYMMDD-HHMMSS.zip` |
| log | `C:\backup\backup.log` |
| เก็บย้อนหลัง | **30 วัน** (ลบ `.zip` ที่เก่ากว่านั้นอัตโนมัติ) |
| ขนาดจริง | dump 62.6 MB → zip **7.45 MB** (~8.4 เท่า) ใช้เวลาราว 6 วินาที |

**หลักการที่ใช้ในสคริปต์**
- รหัสผ่านอ่านจาก `C:\emoneys\.env` ตอนรัน **ไม่ hardcode** ไว้ในไฟล์
- `--single-transaction` → ไม่ล็อกตาราง เว็บใช้งานได้ตามปกติระหว่างดัมป์
- ตรวจ 3 ชั้นก่อนถือว่าสำเร็จ: exit code ของ `mysqldump`, บรรทัดสุดท้ายต้องเป็น
  `Dump completed`, และ `.zip` ต้องสร้างสำเร็จ+ขนาดสมเหตุผล — **ลบ `.sql` ต่อเมื่อผ่านครบ**
- ล้มเหลวเมื่อไหร่เขียน `!!! BACKUP FAILED:` ลง log และ exit 1
  (Task Scheduler เก็บเป็น `LastTaskResult`)

**ทดสอบแล้ว** สั่งรันจริง 13 ส.ค. 2569 14:34 → `LastTaskResult = 0`, zip เปิดอ่านได้
และมีไฟล์ `.sql` ขนาด 62.59 MB อยู่ข้างใน

### ⚠️ ข้อจำกัดที่ยังเหลือ

1. **ไฟล์อยู่บนดิสก์ลูกเดียวกับฐานข้อมูล** — ดิสก์เสีย = หายทั้งคู่
   แผนคือเจ้าของระบบ SCP ออกนอกเครื่องเองทุกสัปดาห์
2. **ยังไม่เคยทดสอบ restore จริง** — ต้องใช้ root สร้างฐานชั่วคราวแยกแล้ว import เทียบจำนวนแถว
3. **ไม่มีการแจ้งเตือนเมื่อ backup ล้ม** — ต้องเปิด `backup.log` หรือดู `LastTaskResult` เอง

### คำสั่งที่ใช้บ่อย

ดูสถานะ/ผลรันล่าสุด:

```powershell
Get-ScheduledTaskInfo -TaskName emoneys-db-backup
Get-Content C:\backup\backup.log -Tail 20
```

สั่งรันนอกรอบ:

```powershell
Start-ScheduledTask -TaskName emoneys-db-backup
```

ดึงไฟล์ออกนอกเครื่อง (รันจากเครื่องปลายทาง — เปลี่ยนชื่อไฟล์กับโฟลเดอร์ปลายทางตามจริง):

```powershell
scp -i C:\Users\azimuthotg\.ssh\emoneys_prod Administrator@110.78.83.103:"C:/backup/emoneys-20260813-143406.zip" D:\
```

ดูว่ามีไฟล์อะไรให้ดึงบ้าง:

```powershell
ssh -i C:\Users\azimuthotg\.ssh\emoneys_prod Administrator@110.78.83.103 "dir C:\backup"
```
