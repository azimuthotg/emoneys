# Administrative & Management Features User Manual
## Receipt Management System - Nakhon Phanom University

---

## Table of Contents
1. [User Management](#user-management)
2. [Department Management](#department-management)
3. [Dashboard Features](#dashboard-features)
4. [System Configuration](#system-configuration)
5. [Key Management URLs](#key-management-urls)

---

## User Management

### Overview
The User Management system provides administrators with complete control over user access, approval workflows, and role assignments. The system supports staff and student accounts with hierarchical approval workflows.

### User Approval Workflow

#### User Status Flow
```
New User Registration
    ↓
Pending Approval (awaiting admin review)
    ├→ Approve → Approved (Active - can login)
    └→ Reject → Rejected (Inactive - cannot login)

Active User
    ├→ Suspend → Suspended (Inactive - temporary)
    └→ Activate → Back to Approved
```

#### Approval Process Steps

1. **New User Registration**
   - Users register with ID card number and password
   - System validates against NPU AD/API
   - User status set to "Pending Approval"
   - User cannot login until admin approval

2. **Admin Review** (User Management Page)
   - View all pending users with complete details
   - Search by name, ID card number, or department
   - Filter by department
   - Review staff type, position, and organization info

3. **Approval Actions**
   - Individual approval: Click green checkmark button
   - Individual rejection: Click red X button
   - Bulk approval: Select multiple users, click "อนุมัติที่เลือก" button
   - Bulk rejection: Select multiple users, click "ปฏิเสธที่เลือก" button

4. **Post-Approval**
   - User moves to "Approved" tab
   - User receives confirmation and can login
   - User is assigned a role if needed
   - User can create receipts based on role permissions

#### User Status States

| Status | Can Login | Can Edit | Visible In | Actions Available |
|--------|-----------|----------|-----------|------------------|
| **Pending** | ❌ No | ❌ No | Pending tab | Approve / Reject |
| **Approved** | ✅ Yes | ✅ Yes | Active tab | Edit Roles / Suspend |
| **Suspended** | ❌ No | ❌ No | Suspended tab | Reactivate |
| **Rejected** | ❌ No | ❌ No | All Users tab | None |

### Role Assignment Process

#### Understanding Roles

The system uses a flexible role-based permission system:

**Available Roles:**

1. **Basic User (ผู้ใช้พื้นฐาน)**
   - Can create receipts
   - Can view own receipts
   - Cannot approve or manage others' receipts
   - Permissions: receipt_create, receipt_view_own

2. **Department Manager (ผู้ดูแลหน่วยงาน)**
   - Can manage receipts in their department
   - Can approve edit/cancel requests
   - Can view all department receipts
   - Permissions: receipt_view_department, receipt_cancel_department, receipt_edit_approve

3. **Approver (ผู้อนุมัติ)**
   - Can approve edit requests
   - Can view all receipts
   - Can manage receipt lifecycle
   - Permissions: receipt_edit_approve, receipt_view_all

4. **System Admin (ผู้ดูแลระบบ)**
   - Full system access
   - Can manage users, departments, templates, settings
   - Can access all reports
   - Automatically assigned to superuser accounts

#### Assigning Roles to Users

1. **From User Management Page:**
   - Navigate to: `/accounts/management/users/`
   - Go to "Approved Users" tab
   - Click "Edit Roles" button (user-tag icon) for each user
   - Modal opens: "Role Assignment"

2. **Role Assignment Modal:**
   - Shows user information: name, ID, department
   - Displays all available roles as checkboxes
   - Each role shows description
   - Select desired roles
   - Click "บันทึกสิทธิ์" to save

3. **Multiple Roles:**
   - Users can have multiple roles simultaneously
   - Permissions combine across all assigned roles
   - System evaluates highest permission level

4. **Bulk Role Assignment:**
   - Select multiple users in "Approved Users" tab
   - Click "กำหนดสิทธิ์" button at top
   - Assign same role to multiple users efficiently

#### Permission Details

**Permission Structure:**

| Permission | Code | Description |
|-----------|------|-------------|
| Create Receipt | receipt_create | Can create new receipts |
| View Own Receipts | receipt_view_own | View only own receipts |
| Edit Request | receipt_edit_request | Submit edit requests |
| View Edit Requests | receipt_edit_request_view | See own edit requests |
| Approve Edits | receipt_edit_approve | Approve edit requests |
| View Department | receipt_view_department | View dept receipts |
| Cancel Department | receipt_cancel_department | Cancel dept receipts |
| View All | receipt_view_all | View all receipts |
| Export | receipt_export | Export receipt data |
| User Management | user_manage | Manage users |
| Role Management | role_manage | Manage roles/permissions |
| View Reports | report_view | Access reports |
| System Config | system_config | Configure system |

### Department Assignment

#### Department Structure

**NPU Integration:**
- Departments sourced from NPU AD (Active Directory)
- Department names auto-populated from NPU
- Admin assigns department abbreviations (codes)

#### Assigning Users to Departments

1. **Automatic Assignment:**
   - When user logs in from NPU, department auto-populated
   - If no NPU data, manually assign or leave blank

2. **Manual Assignment:**
   - Edit user in Django Admin
   - Set "department_internal_name" field
   - Or view in User Details modal

3. **Department-Based Permissions:**
   - Users see only their department's receipts
   - Department managers oversee their department
   - Admins can see all departments

### User Activation and Suspension

#### Activation (Reactivating Suspended Users)

1. **From User Management - Suspended Tab:**
   - Find suspended user
   - Click green "Activate" button
   - Confirm action
   - User status changes to "Approved"
   - User can login again

2. **Bulk Activation:**
   - Select multiple suspended users
   - Click "เปิดใช้งานที่เลือก" button
   - Confirm bulk action
   - All selected users reactivated

#### Suspension (Temporarily Deactivating Users)

1. **From User Management - Approved Users Tab:**
   - Find active user
   - Click red "Suspend" button
   - Confirm suspension
   - User status changes to "Suspended"
   - User cannot login

2. **Why Suspend:**
   - Temporary leave of absence
   - Investigation or security review
   - Performance issues needing review
   - Role change pending

#### Rejection (Denying Access)

1. **Rejecting Pending Users:**
   - Go to Pending Users tab
   - Click red X button
   - User marked as "Rejected"
   - User cannot login
   - Cannot reactivate directly (requires admin action)

### User Management Interface

#### Main User Management Page

**URL:** `/accounts/management/users/`

**Features:**

1. **Statistics Cards:**
   - Total Users: All users in system
   - Pending Approval: Awaiting review
   - Approved Users: Active accounts
   - Suspended Users: Inactive temporarily

2. **Tab Navigation:**

   **Tab 1: Approved Users (Active)**
   - Shows all active users
   - Includes active staff and active students
   - Search box for name/ID
   - Department filter dropdown
   - Role filter dropdown
   - Can edit roles for any user
   - Can suspend individual users
   - Can view full details
   - Bulk role assignment
   - Bulk suspension

   **Tab 2: Pending Approval**
   - Shows users awaiting admin review
   - Registration date/time shown
   - Position and department displayed
   - Approve: Individual or bulk
   - Reject: Individual or bulk
   - View details for verification
   - Search and department filter

   **Tab 3: Suspended Users**
   - Shows temporarily inactive users
   - Shows date suspended
   - Shows suspension reason if available
   - Can reactivate individually or in bulk
   - View details to verify
   - Search and department filter

   **Tab 4: All Users**
   - Combined view of all users
   - Status column shows current state
   - Role-based filter
   - Status filter
   - Can bulk export
   - Quick view only (no edit actions here)

#### User Details Modal

**Accessed by:** Clicking eye icon next to any user

**Information Displayed:**

- Full Name (Thai and English if available)
- ID Card Number / Staff Code
- Email Address
- Phone Number
- Department / Faculty
- Position / Program
- User Type (Staff/Student)
- Current Roles
- Approval Status
- Account Status
- Date Joined
- Last Login
- NPU Sync Information

#### Search and Filter

- **Search Box:** Real-time search by:
  - Full name (any part)
  - ID card number
  - Email address
  - Username
  
- **Department Filter:** Filter by NPU department

- **Role Filter:** Filter by assigned role

- **Status Filter:** Pending/Approved/Suspended/All

---

## Department Management

### Overview
Department management allows administrators to organize NPU departments, assign abbreviated codes for receipt numbering, and manage department-specific settings.

### Department Structure

#### NPU Department Integration

**Information Source:**
- Departments automatically synced from NPU AD
- Shows all departments where users exist
- Cannot edit department name (comes from NPU)

**Department Data:**

| Field | Source | Editable |
|-------|--------|----------|
| Full Name | NPU AD | ❌ No |
| Department Code (Abbreviation) | Admin | ✅ Yes |
| Address | Admin | ✅ Yes |
| Postal Code | Admin | ✅ Yes |
| Phone Number | Admin | ✅ Yes |
| Active Status | Admin | ✅ Yes |

### Department Code Assignment

#### Code Purpose
- Used in receipt numbering system
- Example: `REG-2025-0001` (REG = code)
- Must be unique across system
- Typical length: 3-5 characters
- Format: Uppercase letters, numbers, underscores

#### Assigning Department Codes

1. **From Department Management Page:**
   - URL: `/accounts/management/departments/`
   - Select department without code
   - Click "กำหนดชื่อย่อ" button

2. **Code Assignment Form:**
   - Select department from NPU AD dropdown
   - Enter abbreviation code (auto-uppercase)
   - Validate format (letters/numbers/underscore only)
   - Fill address information (optional but recommended)
   - Set active status
   - Save

3. **Common Codes:**
   - Registry/Registration: `REG`
   - Finance: `FIN`
   - Human Resources: `HR`
   - Accounting: `ACC`
   - Administration: `ADM`

#### Code Editing

1. **Edit Existing Code:**
   - Department Management page
   - Click "Edit" button (pencil icon)
   - Modal shows current code
   - Modify abbreviation
   - Update address/phone info
   - Save changes

2. **Cannot Edit:**
   - Department name (from NPU)
   - Department list (from NPU)

### Volume Management

#### Understanding Document Volumes

**Volume Definition:**
- Container for sequential receipt numbering
- One volume per department per fiscal year
- Auto-created on first receipt creation
- Can hold up to 9,999 receipts (configurable)

**Volume Status:**
- **Active:** Currently in use, accepting new receipts
- **Closed:** No new receipts can be issued
- **Archived:** Historical/past volumes

#### Fiscal Year System

**Thai Fiscal Year:**
- Start: October 1 (1 ต.ค.)
- End: September 30 (30 ก.ย.)
- Example: Fiscal Year 2568 (2568 = BE 2568 = CE 2025)

**Volume Auto-Generation:**
- System automatically creates volumes
- Triggered on first receipt of fiscal year
- Department-specific volumes
- Based on fiscal year dates

#### Volume Monitoring

1. **From Document Numbering Page:**
   - URL: `/accounts/management/document-numbering/`

2. **Volume Statistics Displayed:**
   - Total volumes in system
   - Active volumes count
   - Total documents issued
   - System coverage percentage

3. **Per-Volume Information:**
   - Volume Code (e.g., `REG68`)
   - Department Name
   - Volume Status
   - Usage statistics:
     - Documents issued
     - Documents remaining
     - Capacity percentage
   - Latest receipt number
   - Latest receipt date

#### Closing Volumes

**When to Close:**
- Fiscal year ended, starting new year
- Department needs new numbering sequence
- Volume nearly full (auto-alerts at 90%)
- System maintenance

**How to Close:**

1. **From Document Numbering Page:**
   - Find volume in current fiscal year
   - Click "Close" button (lock icon)
   - Modal appears

2. **Close Volume Modal:**
   - Confirms volume and department
   - Optional: Enter reason for closing
   - Click "ปิดเล่ม" to confirm
   - Volume status changes to "Closed"

3. **After Closing:**
   - No new receipts in this volume
   - Automatic next fiscal year volume created
   - Historical volume still accessible for viewing
   - Cannot reopen (permanent)

### Statistics and Monitoring

#### Department Statistics

**Available Metrics:**

1. **Member Count:**
   - Users assigned to department
   - Updated in real-time
   - Displayed in department list

2. **Receipt Statistics:**
   - Total receipts by department
   - Total revenue collected
   - Receipts by status (draft, completed, cancelled)

3. **Volume Usage:**
   - Percentage of current volume used
   - Documents remaining in volume
   - Multiple volumes if needed

4. **Activity Tracking:**
   - Most recent receipt date
   - Most recent edit
   - User activity per department

#### Viewing Department Statistics

1. **From Department Management:**
   - View column shows member count
   - Status shows active/inactive state

2. **From Document Numbering:**
   - View volume usage percentages
   - Department-wise volume breakdown
   - Total documents issued

3. **From Reports:**
   - Revenue summary by department
   - Receipt count by department
   - Trends over time

---

## Dashboard Features

### Admin Dashboard

#### Access
- **URL:** `/accounts/dashboard/` (auto-routes admin users)
- **Permission:** Staff or Superuser only
- **Role:** System administrators

#### Dashboard Components

**1. Welcome Section**
- Greeting with admin name
- System status indicator
- Quick access buttons

**2. Key Statistics**

| Metric | Purpose | Update Frequency |
|--------|---------|-----------------|
| Total Users | System size | Real-time |
| Pending Approvals | Actions needed | Real-time |
| Approved Users | Active accounts | Real-time |
| Total Receipts | System usage | Real-time |

**3. Pending Users Section**

- Display list of users awaiting approval
- Shows full details:
  - ID Card Number
  - Full Name
  - Department
  - Position/Title
  - Date Joined
  - Registration Time

- Quick Actions:
  - Individual approval (green check)
  - Individual rejection (red X)
  - View full details (eye icon)
  - Bulk approval
  - Bulk rejection

**4. Action Buttons**

- Refresh/Sync Data
- Export User Data
- Access Django Admin Interface
- Navigate to User Management

#### Dashboard Workflow

1. **System Admin Logs In:**
   - User marked as staff/superuser
   - Auto-routed to admin dashboard
   - See overview of pending actions

2. **Review Pending Users:**
   - See at-a-glance pending count
   - Can approve directly from dashboard
   - Or navigate to full management page

3. **Take Action:**
   - Approve/Reject pending users
   - Page updates in real-time
   - Statistics refresh automatically
   - Toast notifications confirm actions

### User Dashboard

#### Access
- **URL:** `/accounts/dashboard/` (regular users)
- **Permission:** All authenticated users
- **Default route:** After successful login

#### User Dashboard Components

**1. Welcome Section**
- Personal greeting: "ยินดีต้อนรับ [ชื่อ]"
- Quick stats about own activity

**2. Personal Statistics**

| Stat | Shows |
|------|-------|
| My Receipts (Total) | All receipts created by user |
| My Receipts (This Month) | Receipts created this month |
| My Receipts (Pending) | Draft/incomplete receipts |
| Total Amount | Sum of own receipts |
| Last Receipt | Most recent receipt date |

**3. Recent Activity**

- List of recent receipts
- Can click to view/edit
- Shows receipt number, date, amount, status
- Quick links to common actions

**4. Quick Action Buttons**

- Create New Receipt
- View My Receipts
- View Edit Requests
- View My Pending Approvals
- View Reports
- Download/Print Recent Receipts

**5. Role-Based Features**

**If Department Manager:**
- View department receipts (all)
- Pending approvals for department
- Department statistics
- Team member activity

**If Approver:**
- All pending approvals
- All receipts (view-only)
- System-wide statistics
- Reports access

**If Basic User:**
- Own receipts only
- Edit request status
- Quick receipt creation
- Limited reports

#### Dashboard Information Display

**Receipt Summary Table:**
- Receipt Number
- Recipient Name
- Amount
- Date Created
- Current Status (Draft/Complete/Cancelled)
- Action buttons (View/Edit/Delete/Print)

**Status Indicators:**
- Draft: Gray badge
- Completed: Green badge
- Cancelled: Red badge
- Pending Review: Yellow badge

#### Dashboard Permissions

| Feature | Basic User | Manager | Approver | Admin |
|---------|-----------|---------|----------|-------|
| View Own Receipts | ✅ | ✅ | ✅ | ✅ |
| View Dept Receipts | ❌ | ✅ | ✅ | ✅ |
| View All Receipts | ❌ | ❌ | ✅ | ✅ |
| Create Receipts | ✅ | ✅ | ✅ | ✅ |
| Edit Own Receipts | ✅ | ✅ | ✅ | ✅ |
| Approve Edits | ❌ | ✅ | ✅ | ✅ |
| View Reports | Limited | Dept | System | System |
| Access Admin Tools | ❌ | ❌ | ❌ | ✅ |

---

## System Configuration

### Receipt Templates

#### Template Purpose
- Predefined receipt line items
- Quick selection during receipt creation
- Standardize receipt formats
- Reduce data entry errors

#### Template Components

**Template Fields:**

| Field | Purpose | Type |
|-------|---------|------|
| Name | Display name | Text |
| Category | Grouping/organization | Text |
| Fixed Amount | Preset amount (optional) | Currency |
| Max Amount | Maximum allowed amount | Currency |
| Active Status | Enable/disable template | Boolean |
| Description | Additional info | Text |

#### Managing Templates

**Accessing Template Management:**
- URL: `/manage/templates/`
- Permission: Admin only
- Menu: Admin dropdown → Manage Templates

**Template Operations:**

1. **View All Templates:**
   - List page shows all templates
   - Shows name, category, amount, status
   - Created date shown

2. **Create New Template:**
   - Click "เพิ่มรายการใหม่" button
   - Fill form:
     - Template Name (required)
     - Category (optional)
     - Fixed Amount (if applicable)
     - Max Amount (if applicable)
     - Active status (default: on)
   - Save

3. **Edit Template:**
   - Click edit button (pencil icon)
   - Modify fields
   - Update status
   - Save changes
   - Changes apply to new receipts only

4. **Delete Template:**
   - Click delete button (trash icon)
   - Confirm deletion
   - Template removed from system
   - Existing receipts using template unaffected

#### Template Usage in Receipts

**When Creating Receipt:**
- User can select template
- Template populates line item
- Amount can be overridden
- Multiple templates per receipt

### Document Numbering Configuration

#### Numbering System Overview

**Format:**
```
[Department-Code]-[Fiscal-Year]-[Sequential-Number]
Example: REG-2025-0001
         └─ Department Code
             └─ Fiscal Year
                 └─ Sequential in volume
```

#### Fiscal Year Settings

**Thai Fiscal Year (ปีงบประมาณ):**
- Start Date: October 1, 2024 (1 ต.ค. 2567)
- End Date: September 30, 2025 (30 ก.ย. 2568)
- Stored as: 2568 (Buddhist Era)

**Year Transition:**
- Automatic year change on October 1
- New volumes created automatically
- Notification sent to admins
- Old volumes archived

#### Monitoring Document Numbering

**From Document Numbering Page:**
- URL: `/accounts/management/document-numbering/`

**Information Displayed:**

1. **Fiscal Year Info:**
   - Current fiscal year
   - Start and end dates
   - Days passed this year
   - Days remaining
   - Progress percentage
   - Status (Early/Mid/Late)

2. **System Statistics:**
   - Total volumes created
   - Active volumes (in use)
   - Closed volumes (archived)
   - Total documents issued
   - Coverage percentage

3. **Volume-by-Volume Details:**
   - Volume code (e.g., REG68)
   - Department name
   - Current status (Active/Closed)
   - Documents issued in volume
   - Maximum capacity (usually 9,999)
   - Usage percentage
   - Latest receipt number and date

4. **Warnings & Alerts:**
   - Volumes reaching capacity (90%+)
   - Nearly-ended fiscal years (30 days left)
   - Missing departments without volumes
   - Errors in numbering sequence

#### Volume Capacity and Management

**Default Settings:**
- Max documents per volume: 9,999
- Warning threshold: 90% full
- Auto-increment: Yes

**Monitoring Volume Fullness:**

| Usage | Status | Action Needed |
|-------|--------|--------------|
| 0-80% | Normal | None |
| 80-90% | Warning | Plan closure |
| 90%+ | Critical | Close volume soon |
| 100% | Exceeded | Must close |

**Auto-Alerts:**
- System notifies admin at 90% capacity
- Warns users cannot create new receipts
- Suggests volume closure
- Prevents data loss from overfull volume

#### Closing and Archiving

**Close Volume (End of Cycle):**
1. Department completes fiscal year
2. Admin navigates to Document Numbering
3. Selects active volume
4. Clicks close button
5. Optional: Enters reason for closing
6. Confirms action
7. Volume status → Closed
8. Next fiscal year volume auto-created

**Archive Volume (Long-term Storage):**
- Status changes to "archived"
- Still accessible for viewing
- Cannot create new receipts
- Available for historical reports

### Settings Management

#### Accessing System Settings
- URL: `/admin/` (Django Admin Interface)
- Permission: Superuser/Admin only

#### Configuration Areas

**1. User Settings:**
- User approval workflow
- Password requirements
- Login session timeout
- Two-factor authentication (future)

**2. Department Settings:**
- Active departments list
- Department address information
- Department-user associations

**3. Receipt Settings:**
- Template management
- Receipt numbering format
- Fiscal year configuration
- Receipt approval workflow

**4. Permissions Settings:**
- Role definitions
- Permission assignments
- Default role for new users
- Role-based access controls

**5. API & Integration Settings:**
- NPU AD connection
- NPU API configuration
- API keys (if using external services)
- Sync frequency and logs

**6. Notifications:**
- Email notification settings
- Alert thresholds
- Admin notification recipients
- User notification preferences

---

## Key Management URLs

### Main Administrative URLs

| Page | URL | Permission | Purpose |
|------|-----|-----------|---------|
| Admin Dashboard | `/accounts/dashboard/` | Staff/Admin | Overview & pending approvals |
| User Management | `/accounts/management/users/` | Admin | Manage users & roles |
| Department Management | `/accounts/management/departments/` | Admin | Configure departments |
| Document Numbering | `/accounts/management/document-numbering/` | Admin | Monitor volumes |
| Roles & Permissions | `/accounts/admin/roles-permissions/` | Admin | Manage role system |
| Receipt Templates | `/manage/templates/` | Admin | Configure templates |
| Audit Log | `/accounts/reports/audit-log/` | Admin | View activity history |
| User Activity Log | `/accounts/management/user-activity-log/` | Admin | Track logins/logouts |

### User Management Sub-URLs

**AJAX Endpoints (for internal use):**

| Endpoint | Method | Purpose | Return |
|----------|--------|---------|--------|
| `/accounts/management/approve-user/{id}/` | POST | Approve user | JSON |
| `/accounts/management/reject-user/{id}/` | POST | Reject user | JSON |
| `/accounts/management/suspend-user/{id}/` | POST | Suspend user | JSON |
| `/accounts/management/activate-user/{id}/` | POST | Reactivate user | JSON |
| `/accounts/management/user-details/{id}/` | GET | Get user details modal | HTML |
| `/accounts/management/user/{id}/roles/` | GET/POST | Get/set user roles | JSON |
| `/accounts/management/available-roles/` | GET | List all roles | JSON |

### Department Management Sub-URLs

| Endpoint | Method | Purpose | Return |
|----------|--------|---------|--------|
| `/accounts/management/department/create/` | POST | Create department | JSON |
| `/accounts/management/department/{id}/edit/` | GET/POST | Edit department | JSON |
| `/accounts/management/department/{id}/delete/` | POST | Delete department | JSON |
| `/accounts/management/department/{id}/activate/` | POST | Activate department | JSON |
| `/accounts/management/department/{id}/deactivate/` | POST | Deactivate department | JSON |
| `/accounts/management/available-npu-departments/` | GET | List NPU departments | JSON |

### Document & Volume Management URLs

| Endpoint | Method | Purpose | Return |
|----------|--------|---------|--------|
| `/accounts/management/volume/{id}/close/` | POST | Close document volume | JSON |
| `/accounts/management/document-numbering/` | GET | View volume dashboard | HTML |

### Permission-Based URL Access

**Admin-Only URLs:**
- `/accounts/management/users/`
- `/accounts/management/departments/`
- `/accounts/management/document-numbering/`
- `/accounts/admin/roles-permissions/`
- `/manage/templates/`
- `/accounts/management/user-activity-log/`

**User-Accessible URLs:**
- `/accounts/dashboard/` (different content based on role)
- `/accounts/receipt/list/`
- `/accounts/receipt/create/`
- `/accounts/reports/`

**Public URLs (No Login):**
- `/accounts/` (redirects to login)
- `/accounts/login/`
- `/accounts/check/{code}/{date}/{number}/` (QR code verification)

---

## Troubleshooting & Common Tasks

### Common Administrative Tasks

#### Approving New Users
1. Go to Admin Dashboard or User Management
2. Find user in Pending tab
3. Review details (name, department, position)
4. Click green checkmark to approve
5. User receives notification and can login

#### Adding User to Department
1. User logs in from NPU
2. Department auto-populated from NPU AD
3. If manual entry needed:
   - Edit user in Admin
   - Set "department_internal_name"
   - Save

#### Assigning Roles
1. Go to User Management
2. Find user in Approved Users
3. Click Edit Roles button
4. Select desired roles (checkboxes)
5. Click Save
6. User permissions update immediately

#### Creating Receipt Template
1. Go to Manage Templates
2. Click "Add New"
3. Enter name, category
4. Set amount (if fixed)
5. Mark active
6. Save

#### Closing Fiscal Year Volume
1. Go to Document Numbering
2. Find volume to close
3. Click lock/close button
4. Optional: enter reason
5. Confirm action
6. Volume closed, new volume auto-created

#### Exporting User Data
1. Go to User Management
2. Select All Users tab
3. Click Export button
4. Choose format (Excel/CSV)
5. File downloads

#### Viewing Audit Trail
1. Go to Reports
2. Click Audit Log
3. Filter by date/user/action
4. View all system changes
5. Export if needed

---

## System Limits & Constraints

**User Management:**
- Max users per system: Unlimited (database dependent)
- Max roles per user: Unlimited
- Session timeout: Configurable (default 2 weeks)

**Department Management:**
- Max departments: Per NPU AD
- Department code length: 3-20 characters
- Unique code requirement: Required

**Document Volumes:**
- Default max documents per volume: 9,999
- Min/Max fiscal years: Configurable
- Volume closure: Permanent (cannot reopen)

**Templates:**
- Max templates: Unlimited
- Template name length: 255 characters
- Max template amount: 9,999,999.99 baht

---

## Support & References

**For More Information:**
- See Receipt Management User Manual
- Contact System Administrator
- View Django Admin documentation
- Check API Integration Guide

**Key Database Models:**
- User (Custom user model)
- Role & Permission (Role-based access)
- Department (Organization structure)
- DocumentVolume (Receipt numbering)
- Receipt (Receipt records)
- ReceiptTemplate (Line item templates)
- ReceiptChangeLog (Audit trail)
- UserActivityLog (Login tracking)

---

*Document Last Updated: October 18, 2025*
*Version: 2.0*
*System: Receipt Management System - Nakhon Phanom University*

