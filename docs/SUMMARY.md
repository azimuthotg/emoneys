# Administrative & Management Features Overview
## Nakhon Phanom University Receipt Management System

**Exploration Date:** October 18, 2025
**Thoroughness Level:** Medium
**Status:** Complete with Comprehensive Documentation

---

## Summary of Findings

### 1. USER MANAGEMENT

**User Approval Workflow:**
- New users register and are set to "Pending Approval"
- Admin must approve in User Management (`/accounts/management/users/`)
- Status flow: Pending → Approved → (Suspended/Active)
- Individual and bulk approval/rejection supported
- User details modal shows complete information

**Role Assignment:**
- 4 main roles: Basic User, Department Manager, Approver, System Admin
- Users can have multiple roles simultaneously
- Roles managed via modals in User Management
- Permissions combine from all assigned roles
- Bulk role assignment for multiple users

**Role Capabilities:**

| Role | Key Permissions | Access |
|------|-----------------|--------|
| Basic User | Create/view own receipts | Limited dashboard |
| Department Manager | Manage department receipts, approve edits | Department-level access |
| Approver | Approve all edits, view all receipts | System-level access |
| System Admin | Full system control | All features |

**User Status Management:**
- **Approved:** Can login and use system
- **Pending:** Awaiting admin review
- **Suspended:** Temporarily inactive
- **Rejected:** Permanently denied access

**Department Assignment:**
- Auto-populated from NPU AD for staff
- Can be manually assigned if needed
- Users see only their department's receipts (except admins)

---

### 2. DEPARTMENT MANAGEMENT

**Department Structure:**
- Departments sourced from NPU Active Directory
- Admin assigns unique abbreviation codes (3-5 characters)
- Department info stored with address, postal code, phone
- Can be activated/deactivated

**Department Code Examples:**
- REG = Registration
- FIN = Finance
- HR = Human Resources
- ACC = Accounting
- ADM = Administration

**Department Statistics:**
- Member count (users in department)
- Receipt statistics
- Volume usage percentages
- Activity tracking

**Access:** `/accounts/management/departments/`

---

### 3. DOCUMENT VOLUME & NUMBERING

**Numbering Format:**
```
[DEPT-CODE]-[FISCAL-YEAR]-[SEQUENCE]
Example: REG-2025-0001
```

**Fiscal Year System:**
- Thai Fiscal Year: October 1 - September 30
- Example: FY 2568 (Buddhist Era)
- Volumes auto-created on first receipt
- One volume per department per fiscal year

**Volume Management:**
- Default capacity: 9,999 receipts per volume
- Statuses: Active, Closed, Archived
- Warning alerts at 90% capacity
- Can manually close volumes
- Closed volumes still accessible for viewing

**Monitoring Available From:**
- Document Numbering page: `/accounts/management/document-numbering/`
- Shows all volumes with usage statistics
- Real-time fiscal year countdown
- Department coverage percentage

---

### 4. DASHBOARD FEATURES

**Admin Dashboard** (`/accounts/dashboard/` for staff users)
- Key metrics: Total users, pending approvals, approved users, total receipts
- Pending users list for quick action
- Individual and bulk approval/rejection
- Statistics refresh in real-time
- Toast notifications for actions

**User Dashboard** (regular users)
- Personal statistics (receipts created, totals, pending)
- Recent activity/receipts
- Quick action buttons
- Role-based content (managers see dept receipts, etc.)

**Permission-Based Views:**
- Admins see pending approvals and statistics
- Managers see department-specific data
- Users see only their own data
- Approvers see all receipts

---

### 5. SYSTEM CONFIGURATION

**Receipt Templates**
- Access: `/manage/templates/`
- Used as predefined line items
- Fields: Name, Category, Fixed Amount, Max Amount
- Can create, edit, delete templates
- Template status: Active/Inactive

**Configuration Areas:**
1. User Settings (approval workflow, timeouts)
2. Department Settings (departments, addresses)
3. Receipt Settings (numbering, templates)
4. Permission Settings (roles, permissions)
5. API Integration (NPU AD, NPU API)
6. Notifications (email, alerts)

---

## Key Administrative URLs

| Function | URL | Method |
|----------|-----|--------|
| Admin Dashboard | `/accounts/dashboard/` | GET |
| User Management | `/accounts/management/users/` | GET |
| Department Mgmt | `/accounts/management/departments/` | GET/POST |
| Document Numbering | `/accounts/management/document-numbering/` | GET |
| Templates | `/manage/templates/` | GET/POST |
| Audit Log | `/accounts/reports/audit-log/` | GET |
| Django Admin | `/admin/` | GET |
| Approve User | `/accounts/management/approve-user/{id}/` | POST |
| Reject User | `/accounts/management/reject-user/{id}/` | POST |
| Suspend User | `/accounts/management/suspend-user/{id}/` | POST |
| Get User Details | `/accounts/management/user-details/{id}/` | GET |
| Set User Roles | `/accounts/management/user/{id}/roles/` | GET/POST |
| Available Roles | `/accounts/management/available-roles/` | GET |
| Create Department | `/accounts/management/department/create/` | POST |
| Edit Department | `/accounts/management/department/{id}/edit/` | GET/POST |
| Delete Department | `/accounts/management/department/{id}/delete/` | POST |
| Activate Dept | `/accounts/management/department/{id}/activate/` | POST |
| Deactivate Dept | `/accounts/management/department/{id}/deactivate/` | POST |
| Close Volume | `/accounts/management/volume/{id}/close/` | POST |

---

## File Structure

### Key Model Files
- `/mnt/c/projects/emoneys/accounts/models.py` - User, Department, Role, DocumentVolume, Receipt models
- `/mnt/c/projects/emoneys/accounts/admin.py` - Django admin configurations
- `/mnt/c/projects/emoneys/accounts/views.py` - View logic for management pages
- `/mnt/c/projects/emoneys/accounts/urls.py` - URL routing

### Key Template Files
- `/mnt/c/projects/emoneys/templates/accounts/user_management.html` - User management interface
- `/mnt/c/projects/emoneys/templates/accounts/admin_dashboard.html` - Admin dashboard
- `/mnt/c/projects/emoneys/templates/accounts/department_management.html` - Department management
- `/mnt/c/projects/emoneys/templates/accounts/document_numbering.html` - Volume monitoring
- `/mnt/c/projects/emoneys/templates/accounts/receipt_templates_list.html` - Template management

---

## Database Models

**User Model (Custom AbstractUser)**
- ldap_uid (unique identifier)
- npu_staff_id, full_name, department
- approval_status (pending/approved/rejected/suspended)
- Roles managed via UserRole junction table

**Role Model**
- name (unique role identifier)
- display_name, description
- permissions (M2M to Permission)
- department_scope (optional, for scoped roles)

**Permission Model**
- name (unique permission code)
- description
- 13 system permissions defined

**Department Model**
- name (from NPU AD)
- code (admin-assigned abbreviation)
- address, postal_code, phone
- is_active status

**DocumentVolume Model**
- department (FK)
- fiscal_year
- volume_code (unique)
- status (active/closed/archived)
- last_document_number, max_documents
- fiscal_year_start, fiscal_year_end

---

## Permission System

**13 Core Permissions:**

Basic:
- receipt_create
- receipt_view_own
- receipt_edit_request

Department-Level:
- receipt_view_department
- receipt_cancel_department
- receipt_edit_approve

System-Level:
- receipt_view_all
- receipt_export
- user_manage
- role_manage
- report_view
- system_config

---

## Statistics & Monitoring

**User Statistics Tracked:**
- Total users
- Pending approvals
- Approved users
- Suspended users
- By department
- By role

**Department Statistics Tracked:**
- User count per department
- Receipt count
- Revenue total
- Volume usage percentage

**System Statistics:**
- Total volumes
- Active volumes
- Documents issued
- Coverage percentage
- Fiscal year progress

---

## Action Workflows

### User Approval Workflow
1. User registers → Status: Pending
2. Admin reviews in User Management
3. Admin clicks approve/reject
4. If approved: Status: Approved, is_active: True
5. User can now login and be assigned roles
6. User creates receipts based on role permissions

### Role Assignment Workflow
1. Admin finds approved user
2. Clicks "Edit Roles" button
3. Selects role checkboxes
4. Saves changes
5. User permissions updated immediately
6. User's receipt creation and access updated

### Department Setup Workflow
1. Users from NPU AD create departments
2. Admin navigates to Department Management
3. Admin clicks "Assign Code" for department
4. Enters abbreviation code
5. Fills address information
6. Saves
7. Department ready to issue receipts

### Volume Management Workflow
1. User creates first receipt for department/fiscal year
2. System auto-creates volume with code
3. Receipts numbered sequentially in volume
4. Admin monitors usage in Document Numbering
5. At 90%+: System alerts admin
6. Admin manually closes volume when full
7. Next fiscal year: System auto-creates new volume

---

## User Experience Flows

### For Admins
- Login → Dashboard (auto-route if staff)
- Review pending users
- Approve/reject as needed
- Manage departments
- Configure system
- Monitor volumes and capacity
- View audit trails

### For Managers
- Login → Dashboard (see dept data)
- View department receipts
- Approve edit requests
- Cancel receipts if needed
- View department statistics

### For Basic Users
- Login → Dashboard (personal view)
- Create receipts
- View own receipts
- Submit edit requests
- Limited reporting

---

## Strengths of Current Implementation

1. **Flexible Role System:** Users can have multiple roles with combined permissions
2. **Auto-Generated Volumes:** Fiscal year volumes created automatically on first use
3. **Real-Time Statistics:** Dashboard stats update in real-time
4. **Comprehensive Audit Trail:** All changes tracked in ChangeLog
5. **Bulk Operations:** Can approve/assign roles to multiple users at once
6. **NPU Integration:** Auto-syncs with NPU AD for user/department data
7. **Department-Based Access Control:** Users see only their department's data
8. **Fiscal Year Management:** Thai fiscal year system properly implemented

---

## Documents Provided

1. **admin_management_manual.md** - Full 300+ line comprehensive manual
   - Detailed workflows
   - Step-by-step instructions
   - All features documented
   - Troubleshooting guide
   - System limits

2. **admin_quick_reference.md** - Quick reference card
   - Fast navigation paths
   - Quick-step procedures
   - Status colors and meanings
   - Common issues and solutions
   - First-time setup checklist

3. **SUMMARY.md** (this file) - Overview document
   - High-level overview
   - Key findings summary
   - File structure
   - Permission matrix
   - Workflow descriptions

---

## Recommendations for User Manual

1. **Add Screenshots:** Include UI screenshots for each section
2. **Video Tutorials:** Consider screen recordings for common tasks
3. **FAQ Section:** Expand troubleshooting with more scenarios
4. **Permission Matrix:** Detailed table of role permissions (provided)
5. **Integration Guide:** Document NPU AD/API integration setup
6. **Backup Procedures:** Document system backup workflows
7. **Report Generation:** Document report features and exports
8. **Mobile Access:** Note PWA/mobile functionality

---

## Conclusion

The Receipt Management System has a well-designed administrative interface with:
- Comprehensive user management and approval workflows
- Flexible role-based permission system
- Department-based organization and access control
- Automatic document volume management
- Real-time monitoring and statistics
- Efficient bulk operations
- Clean, intuitive user interface

The system supports both staff (via NPU AD) and student authentication, with proper approval workflows and role-based access control throughout. All features are documented in the provided manual files.

---

**Document Summary Generated:** October 18, 2025
**Total Documentation Pages:** 4
**Code Exploration Depth:** Medium
**Ready for User Manual Publication:** Yes

