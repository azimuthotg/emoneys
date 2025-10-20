#!/usr/bin/env python
"""
วิเคราะห์การใช้ notification types ในระบบ
"""
import os
import re

def analyze_file(filepath):
    """วิเคราะห์ไฟล์หนึ่งไฟล์"""
    results = {
        'alert': [],
        'confirm': [],
        'modal': [],
        'toast': []
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                # ค้นหา alert()
                if 'alert(' in line and not line.strip().startswith('//'):
                    # ดึงข้อความใน alert
                    match = re.search(r"alert\(['\"](.+?)['\"]\)", line)
                    if match:
                        results['alert'].append((i, match.group(1)))

                # ค้นหา confirm()
                if 'confirm(' in line and not line.strip().startswith('//'):
                    match = re.search(r"confirm\(['\"](.+?)['\"]\)", line)
                    if match:
                        results['confirm'].append((i, match.group(1)))

                # ค้นหา modal
                if 'new bootstrap.Modal' in line or '.modal(' in line:
                    results['modal'].append((i, line.strip()[:60]))

                # ค้นหา toast
                if 'showToast(' in line:
                    results['toast'].append((i, line.strip()[:60]))

    except Exception as e:
        pass

    return results

def main():
    # ใช้ relative path เพื่อรองรับทั้ง Windows และ Linux
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'templates')

    # ตรวจสอบว่า templates directory มีอยู่จริง
    if not os.path.exists(templates_dir):
        print(f"❌ ไม่พบ directory: {templates_dir}")
        return

    summary = {
        'alert': {},
        'confirm': {},
        'modal': {},
        'toast': {}
    }

    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, templates_dir)

                results = analyze_file(filepath)

                for notif_type, items in results.items():
                    if items:
                        if relative_path not in summary[notif_type]:
                            summary[notif_type][relative_path] = []
                        summary[notif_type][relative_path].extend(items)

    # แสดงผล
    print("="*80)
    print("📊 วิเคราะห์การใช้ Notification Types")
    print("="*80)
    print()

    # Alert
    print("🔔 alert() - JavaScript Alert แบบเก่า")
    print("-"*80)
    if summary['alert']:
        total = sum(len(items) for items in summary['alert'].values())
        print(f"พบ {total} ครั้งใน {len(summary['alert'])} ไฟล์")
        for file, items in sorted(summary['alert'].items()):
            print(f"\n  📄 {file}")
            for line_no, msg in items[:3]:  # แสดงแค่ 3 ตัวอย่างแรก
                print(f"     Line {line_no}: {msg[:50]}...")
            if len(items) > 3:
                print(f"     ... และอีก {len(items)-3} ครั้ง")
    else:
        print("  ไม่พบการใช้งาน")

    print("\n")

    # Confirm
    print("❓ confirm() - JavaScript Confirm Dialog")
    print("-"*80)
    if summary['confirm']:
        total = sum(len(items) for items in summary['confirm'].values())
        print(f"พบ {total} ครั้งใน {len(summary['confirm'])} ไฟล์")
        for file, items in sorted(summary['confirm'].items()):
            print(f"\n  📄 {file}")
            for line_no, msg in items[:3]:
                print(f"     Line {line_no}: {msg[:50]}...")
    else:
        print("  ไม่พบการใช้งาน")

    print("\n")

    # Modal
    print("🪟 Bootstrap Modal")
    print("-"*80)
    if summary['modal']:
        total = sum(len(items) for items in summary['modal'].values())
        print(f"พบ {total} ครั้งใน {len(summary['modal'])} ไฟล์")
        print(f"  ไฟล์ที่มี Modal: {', '.join(list(summary['modal'].keys())[:5])}...")
    else:
        print("  ไม่พบการใช้งาน")

    print("\n")

    # Toast
    print("🍞 Toast Notification")
    print("-"*80)
    if summary['toast']:
        total = sum(len(items) for items in summary['toast'].values())
        print(f"พบ {total} ครั้งใน {len(summary['toast'])} ไฟล์")
        print(f"  ไฟล์ที่มี Toast: {', '.join(list(summary['toast'].keys())[:5])}...")
    else:
        print("  ไม่พบการใช้งาน")

    print("\n" + "="*80)
    print("📋 สรุปและแนะนำ")
    print("="*80)

    print("""
🎯 แนะนำการใช้งานแต่ละแบบ:

1. Toast (🍞) - ใช้สำหรับ:
   ✅ แจ้งเตือนสถานะการทำงาน (บันทึกสำเร็จ, ลบสำเร็จ)
   ✅ ข้อความที่ไม่ต้องการ interaction
   ✅ ข้อความสั้นๆ ที่หายไปเอง

2. Modal (🪟) - ใช้สำหรับ:
   ✅ ยืนยันการลบหรือการกระทำสำคัญ
   ✅ แสดงรายละเอียดเพิ่มเติม
   ✅ ฟอร์มกรอกข้อมูล

3. Alert/Confirm (🔔❓) - ควรเลิกใช้:
   ❌ UI ไม่สวย ล้าสมัย
   ❌ บล็อค browser ทั้งหมด
   ❌ ไม่สามารถปรับแต่ง style ได้

💡 แนะนำ: แทนที่ alert() และ confirm() ด้วย Toast หรือ Modal
    """)

    # แนะนำไฟล์ที่ต้องแก้
    if summary['alert']:
        print("\n⚠️  ไฟล์ที่ควรแก้ไข (ใช้ alert อยู่):")
        for file in sorted(summary['alert'].keys())[:10]:
            print(f"   - {file}")

if __name__ == '__main__':
    main()
