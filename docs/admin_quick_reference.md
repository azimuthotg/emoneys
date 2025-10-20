# Administrative Features - Quick Reference Guide
## Nakhon Phanom University Receipt Management System

---

## Quick Navigation

### Main Admin Paths
```
Dashboard (Admin view)      → /accounts/dashboard/
User Management             → /accounts/management/users/
Department Management       → /accounts/management/departments/
Document Numbering          → /accounts/management/document-numbering/
Receipt Templates           → /manage/templates/
Audit Trail                 → /accounts/reports/audit-log/
Django Admin                → /admin/
```

---

## User Approval Quick Steps

### Approve One User
1. Dashboard or User Management → Pending tab
2. Click green checkmark button
3. Confirm action
✅ User can now login

### Bulk Approve Users
1. Pending tab → Select multiple users (checkboxes)
2. Click "อนุมัติที่เลือก" button
3. Confirm
✅ All selected users approved

### Reject User
1. Pending tab → Find user
2. Click red X button
3. Confirm
❌ User cannot access system

### Suspend Active User
1. Approved Users tab → Find user
2. Click red "Suspend" button
3. Confirm
⏸ User temporarily blocked

### Reactivate Suspended User
1. Suspended tab → Find user
2. Click green "Activate" button
3. Confirm
✅ User can login again

---

## Role Assignment Quick Steps

### Assign Role to One User
1. User Management → Approved Users tab
2. Click edit button (user-tag icon)
3. Check desired role(s)
4. Click "บันทึกสิทธิ์"
✅ Roles updated

### Assign Role to Multiple Users
1. Approved Users → Select users
2. Click "กำหนดสิทธิ์" button at top
3. Check role(s)
4. Save
✅ All selected users get role

### View User's Roles
1. Approved Users → Click eye icon
2. Modal shows current roles
3. Can edit from here if needed

---

## Department Management Quick Steps

### Assign Code to Department
1. Department Management page
2. Click "กำหนดชื่อย่อ" for department
3. Enter code (e.g., REG, FIN, HR)
4. Optional: Add address
5. Save
✅ Department ready

### Edit Department Code
1. Department table → Click edit icon
2. Change code/address/phone
3. Save
✅ Updated

### Deactivate Department
1. Find department → Click power-off icon
2. Confirm
⏸ Department cannot issue receipts

### Reactivate Department
1. Find department → Click power-off icon
2. Confirm
✅ Active again

---

## Document Volume Quick Steps

### Monitor Volumes
1. Document Numbering page
2. Check statistics:
   - Total volumes
   - Active volumes
   - Documents issued
   - Coverage %
3. View volume table details

### Close Volume
1. Document Numbering → Find volume
2. Click lock icon
3. Optional: Enter reason
4. Confirm
🔒 Volume closed (automatic new one created)

### Check Volume Usage
1. Volume table → Check usage %
2. Color coding:
   - 0-80% = Green (OK)
   - 80-90% = Yellow (Monitor)
   - 90%+ = Red (Close soon)

---

## Receipt Templates Quick Steps

### Create Template
1. Manage Templates page
2. Click "เพิ่มรายการใหม่"
3. Enter name (required)
4. Optional: Category, fixed amount, max amount
5. Mark active
6. Save
✅ Template ready for use

### Edit Template
1. Find template in list
2. Click edit icon
3. Modify fields
4. Save
✅ Updated

### Delete Template
1. Find template
2. Click delete icon
3. Confirm
❌ Removed

---

## Statistics Overview

### User Statistics
- **Total Users:** All accounts (pending + approved + suspended)
- **Pending:** Awaiting approval
- **Approved:** Active, can login
- **Suspended:** Temporarily inactive

### Department Statistics
- **Members:** Users in department
- **Status:** Active/Inactive
- **Receipts:** Total issued

### Volume Statistics
- **Total Volumes:** System-wide
- **Active:** In use currently
- **Documents Issued:** Total receipts
- **Coverage %:** System-wide percentage

---

## Permission Quick Reference

| Permission | Who Gets It | What Can They Do |
|-----------|-----------|-----------------|
| **receipt_create** | Basic User+ | Create receipts |
| **receipt_view_own** | Basic User+ | See only their receipts |
| **receipt_view_department** | Manager+ | See dept receipts |
| **receipt_view_all** | Approver+ | See all receipts |
| **receipt_edit_approve** | Manager+ | Approve edit requests |
| **receipt_cancel_department** | Manager+ | Cancel dept receipts |
| **user_manage** | Admin | Manage users |
| **system_config** | Admin | Configure system |

---

## Common Issues & Solutions

### "User can't login after approval"
1. Check user in Approved Users tab
2. Verify status shows "Approved"
3. Check if user is_active field = True
4. In worst case: Re-approve user

### "Volume is full (100%)"
1. Go to Document Numbering
2. Find volume at 100%
3. Click close button
4. New volume auto-created
5. Can continue issuing receipts

### "Department not showing in system"
1. User must exist in system
2. Check NPU AD sync
3. Department name must match NPU
4. May need manual assignment

### "Template not showing when creating receipt"
1. Check template is_active = True
2. Check category matches
3. Reload page (browser cache)
4. Contact admin if still missing

---

## Keyboard Shortcuts & Tips

### Search Tips
- Search by: Name, ID number, email
- Partial matches work
- Case-insensitive
- Real-time results

### Bulk Operations
- Click checkbox in header to select all on page
- Ctrl+Click to select individual items
- Buttons appear at top when selected

### Filters
- Department filter: Shows users in that dept
- Role filter: Shows users with role
- Status filter: Pending/Approved/Suspended/All
- Combine filters for precision

### Sort & Export
- Click column headers to sort (sometimes)
- Use Export button for full data
- Works with filters applied
- Exports only visible/filtered data

---

## Role Hierarchy & Permissions

```
Admin (System Admin)
├─ Full access to everything
├─ Manage users
├─ Manage departments
├─ Configure system
└─ Access all reports

Manager (Department Manager)
├─ Approve edits for dept
├─ View all dept receipts
├─ Cancel dept receipts
├─ View dept statistics
└─ Limited admin functions

Approver (ผู้อนุมัติ)
├─ View all receipts
├─ Approve edit requests
├─ Create receipts
└─ View reports

Basic User (ผู้ใช้พื้นฐาน)
├─ Create receipts
├─ View own receipts
├─ Submit edit requests
└─ Limited dashboard
```

---

## Fiscal Year Reference

**Thai Fiscal Year (ปีงบประมาณ):**

| Month | FY 2567 | FY 2568 |
|-------|---------|---------|
| Oct | 2567 ✓ | 2568 ✓ |
| Nov | 2567 | 2568 |
| Dec | 2567 | 2568 |
| Jan | 2567 | 2568 |
| Feb | 2567 | 2568 |
| Mar | 2567 | 2568 |
| Apr | 2567 | 2568 |
| May | 2567 | 2568 |
| Jun | 2567 | 2568 |
| Jul | 2567 | 2568 |
| Aug | 2567 | 2568 |
| Sep | 2567 | 2568 |

**Volume Code Example:** REG68 = Registration, FY 2568

---

## Status Colors & Meanings

### User Status
- 🟢 **Green (Approved):** Active, can login
- 🟡 **Yellow (Pending):** Awaiting approval
- 🔴 **Red (Suspended):** Temporarily blocked
- ⚫ **Gray (Rejected):** Denied access

### Volume Status
- 🟢 **Green (Active):** In use
- ⚫ **Gray (Closed):** No new receipts
- 🔵 **Blue (Archived):** Historical

### Department Status
- 🟢 **Green (Active):** Can issue receipts
- ⚫ **Gray (Inactive):** Cannot issue

---

## Useful Contact Points

| Item | Details |
|------|---------|
| **Support** | Contact System Administrator |
| **NPU Sync Issues** | Check NPU AD Integration |
| **Permission Issues** | Verify role assignment |
| **Database Issues** | Django Admin → System Logs |
| **API Errors** | Check NPU API Configuration |

---

## Checklist: First-Time Admin Setup

- [ ] Review all pending users
- [ ] Approve legitimate users
- [ ] Reject suspicious registrations
- [ ] Assign roles to approved users
- [ ] Assign department codes
- [ ] Create receipt templates
- [ ] Configure fiscal year settings
- [ ] Setup departments
- [ ] Test approval workflow
- [ ] Configure email notifications
- [ ] Review audit logs
- [ ] Create backup

---

## Last Updated
October 18, 2025

---

*For full details, see: Administrative & Management Features User Manual*

