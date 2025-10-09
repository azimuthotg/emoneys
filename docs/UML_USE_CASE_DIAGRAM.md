# 👥 UML Use Case Diagrams - E-Money Voucher System

## 1. Overall System Use Case Diagram

```plantuml
@startuml
!theme plain
title E-Money Voucher System - Overall Use Cases

left to right direction

actor "Basic User" as basic
actor "Department Manager" as dept
actor "Senior Manager" as senior
actor "System Admin" as admin
actor "Public User" as public

rectangle "E-Money Voucher System" {

  package "Receipt Management" {
    usecase "Create Receipt" as UC1
    usecase "View Own Receipts" as UC2
    usecase "Edit Draft Receipt" as UC3
    usecase "Submit Edit Request" as UC4
    usecase "View Edit Requests" as UC5
    usecase "Approve Edit Request" as UC6
    usecase "Reject Edit Request" as UC7
  }

  package "Cancel Management" {
    usecase "Cancel Draft Receipt" as UC8
    usecase "Submit Cancel Request" as UC9
    usecase "View Cancel Requests" as UC10
    usecase "Approve Cancel Request" as UC11
    usecase "Direct Cancel Receipt" as UC12
  }

  package "Department Management" {
    usecase "View Department Receipts" as UC13
    usecase "View Department Reports" as UC14
    usecase "Manage Department Users" as UC15
  }

  package "System Administration" {
    usecase "Manage All Users" as UC16
    usecase "Assign Roles" as UC17
    usecase "Configure System" as UC18
    usecase "View System Reports" as UC19
    usecase "View Audit Logs" as UC20
  }

  package "Public Access" {
    usecase "Verify Receipt QR" as UC21
    usecase "View Public Receipt" as UC22
  }
}

' Basic User relationships
basic --> UC1
basic --> UC2
basic --> UC3
basic --> UC4
basic --> UC5
basic --> UC8
basic --> UC9
basic --> UC10

' Department Manager relationships
dept --> UC1
dept --> UC2
dept --> UC3
dept --> UC4
dept --> UC6
dept --> UC7
dept --> UC12
dept --> UC13
dept --> UC14

' Senior Manager relationships
senior --> UC1
senior --> UC2
senior --> UC6: "Approves Dept Manager\nrequests"
senior --> UC7
senior --> UC11: "Approves Dept Manager\ncancel requests"
senior --> UC12
senior --> UC13
senior --> UC14
senior --> UC15

' Admin relationships
admin --> UC16
admin --> UC17
admin --> UC18
admin --> UC19
admin --> UC20
admin --> UC12: "Can cancel all"

' Public relationships
public --> UC21
public --> UC22

' Inheritance
dept --|> basic
senior --|> dept

note right of UC6
  Approval Rules:
  - Dept Manager: Basic User requests
  - Senior Manager: Dept Manager requests
  - Same department only
end note

note bottom of UC12
  Direct Cancel Permissions:
  - Dept Manager: Own department
  - Senior Manager: Own department
  - Admin: All departments
end note

@enduml
```

---

## 2. Basic User Use Cases

```plantuml
@startuml
!theme plain
title Basic User Use Cases

actor "Basic User" as user

rectangle "Receipt Operations" {
  usecase "Create Receipt" as create
  usecase "Save as Draft" as draft
  usecase "Confirm Receipt" as confirm
  usecase "View Own Receipts" as view
  usecase "Download PDF" as pdf
  usecase "Print Receipt" as print
}

rectangle "Edit Operations" {
  usecase "Edit Draft Receipt" as editDraft
  usecase "Submit Edit Request" as editRequest
  usecase "View Edit Request Status" as viewEdit
  usecase "Withdraw Edit Request" as withdrawEdit
}

rectangle "Cancel Operations" {
  usecase "Cancel Draft Receipt" as cancelDraft
  usecase "Submit Cancel Request" as cancelRequest
  usecase "View Cancel Request Status" as viewCancel
  usecase "Withdraw Cancel Request" as withdrawCancel
}

user --> create
create ..> draft: <<include>>
create ..> confirm: <<include>>

user --> view
view ..> pdf: <<extend>>
view ..> print: <<extend>>

user --> editDraft
user --> editRequest
user --> viewEdit
editRequest ..> withdrawEdit: <<extend>>

user --> cancelDraft
user --> cancelRequest
user --> viewCancel
cancelRequest ..> withdrawCancel: <<extend>>

note right of create
  Permissions Required:
  - receipt_create

  Flow:
  1. Fill recipient details
  2. Add receipt items
  3. Calculate total
  4. Choose: Draft or Completed
end note

note right of editRequest
  Permissions Required:
  - receipt_edit_request

  Conditions:
  - Receipt status = Completed
  - No pending edit request exists

  Approval:
  - Dept Manager (same department)
end note

note right of cancelRequest
  Permissions Required:
  - receipt_cancel_request

  Conditions:
  - Receipt status = Completed
  - No pending cancel request exists

  Approval:
  - Dept Manager (same department)
end note

@enduml
```

---

## 3. Department Manager Use Cases

```plantuml
@startuml
!theme plain
title Department Manager Use Cases

actor "Department Manager" as dept
actor "Basic User" as basic

rectangle "Approval Workflows" {
  usecase "Review Edit Requests" as reviewEdit
  usecase "Approve Edit Request" as approveEdit
  usecase "Reject Edit Request" as rejectEdit
  usecase "Review Cancel Requests" as reviewCancel
  usecase "Approve Cancel Request" as approveCancel
  usecase "Reject Cancel Request" as rejectCancel
}

rectangle "Direct Actions" {
  usecase "Direct Cancel Receipt" as directCancel
  usecase "View Department Receipts" as viewDept
  usecase "Export Department Data" as exportDept
}

rectangle "Own Requests" {
  usecase "Submit Edit Request\n(to Senior Manager)" as selfEdit
  usecase "Submit Cancel Request\n(to Senior Manager)" as selfCancel
}

rectangle "Department Oversight" {
  usecase "View Department Statistics" as stats
  usecase "Generate Reports" as reports
  usecase "Monitor Team Activity" as monitor
}

dept --> reviewEdit
reviewEdit ..> approveEdit: <<extend>>
reviewEdit ..> rejectEdit: <<extend>>

dept --> reviewCancel
reviewCancel ..> approveCancel: <<extend>>
reviewCancel ..> rejectCancel: <<extend>>

dept --> directCancel
dept --> viewDept
viewDept ..> exportDept: <<extend>>

dept --> selfEdit
dept --> selfCancel

dept --> stats
dept --> reports
dept --> monitor

basic --> reviewEdit: "Submits requests"
basic --> reviewCancel: "Submits requests"

note right of approveEdit
  Permission Required:
  - receipt_edit_approve

  Validation:
  1. Same department check
  2. Requester is Basic User
  3. No conflicting requests
  4. Valid receipt status

  Action:
  - Apply changes to receipt
  - Create audit log
  - Notify requester
end note

note right of directCancel
  Permission Required:
  - receipt_cancel_department

  Conditions:
  - Receipt in own department
  - Status = Completed
  - No pending requests

  No approval needed
end note

note bottom of selfEdit
  Dept Manager can:
  1. Submit own edit/cancel requests
  2. Requires Senior Manager approval
  3. Cannot self-approve
  4. Same validation rules apply
end note

@enduml
```

---

## 4. Senior Manager Use Cases

```plantuml
@startuml
!theme plain
title Senior Manager Use Cases

actor "Senior Manager" as senior
actor "Department Manager" as dept

rectangle "High-Level Approvals" {
  usecase "Review Dept Manager\nEdit Requests" as reviewMgrEdit
  usecase "Approve Manager\nEdit Request" as approveMgrEdit
  usecase "Reject Manager\nEdit Request" as rejectMgrEdit
  usecase "Review Dept Manager\nCancel Requests" as reviewMgrCancel
  usecase "Approve Manager\nCancel Request" as approveMgrCancel
  usecase "Reject Manager\nCancel Request" as rejectMgrCancel
}

rectangle "Department Control" {
  usecase "Direct Cancel\nAny Receipt" as directCancel
  usecase "View All Department\nReceipts" as viewAll
  usecase "Override Decisions" as override
  usecase "Manage Department\nSettings" as manageDept
}

rectangle "Reporting & Analytics" {
  usecase "View Department\nPerformance" as performance
  usecase "Generate Advanced\nReports" as advReports
  usecase "Analyze Trends" as trends
  usecase "Review Audit Trail" as audit
}

senior --> reviewMgrEdit
reviewMgrEdit ..> approveMgrEdit: <<extend>>
reviewMgrEdit ..> rejectMgrEdit: <<extend>>

senior --> reviewMgrCancel
reviewMgrCancel ..> approveMgrCancel: <<extend>>
reviewMgrCancel ..> rejectMgrCancel: <<extend>>

senior --> directCancel
senior --> viewAll
senior --> override
senior --> manageDept

senior --> performance
senior --> advReports
senior --> trends
senior --> audit

dept --> reviewMgrEdit: "Submits requests"
dept --> reviewMgrCancel: "Submits requests"

note right of approveMgrEdit
  Permission Required:
  - receipt_edit_approve_manager

  Validation:
  1. Same department
  2. Requester is Dept Manager
  3. Requester has receipt_edit_approve
  4. Valid request status

  Hierarchy:
  Senior Mgr → Dept Mgr → Basic User
end note

note right of directCancel
  Permission Required:
  - receipt_cancel_department
  - receipt_cancel_approve_manager

  Can cancel:
  - Any receipt in department
  - Without approval
  - Regardless of status
  - Creates audit log
end note

note bottom of override
  Special Permissions:
  - Can modify approved requests
  - Can reverse decisions
  - Full department authority
  - Subject to audit
end note

@enduml
```

---

## 5. System Admin Use Cases

```plantuml
@startuml
!theme plain
title System Admin Use Cases

actor "System Admin" as admin

rectangle "User Management" {
  usecase "Approve New Users" as approveUser
  usecase "Reject User Registration" as rejectUser
  usecase "Assign User Roles" as assignRole
  usecase "Suspend User Account" as suspendUser
  usecase "Manage Permissions" as managePerms
}

rectangle "System Configuration" {
  usecase "Configure System Settings" as configSystem
  usecase "Manage Departments" as manageDept
  usecase "Setup Fiscal Year" as setupFY
  usecase "Configure Templates" as configTemplate
  usecase "Manage Document Volumes" as manageVolume
}

rectangle "Cross-Department Operations" {
  usecase "View All Receipts" as viewAllReceipts
  usecase "Cancel Any Receipt" as cancelAny
  usecase "Export All Data" as exportAll
  usecase "Bulk Operations" as bulkOps
}

rectangle "System Monitoring" {
  usecase "View System Reports" as sysReports
  usecase "Monitor User Activity" as monitorActivity
  usecase "Review Audit Logs" as auditLogs
  usecase "Check System Health" as healthCheck
  usecase "Backup & Restore" as backup
}

admin --> approveUser
admin --> rejectUser
admin --> assignRole
admin --> suspendUser
admin --> managePerms

admin --> configSystem
admin --> manageDept
admin --> setupFY
admin --> configTemplate
admin --> manageVolume

admin --> viewAllReceipts
admin --> cancelAny
admin --> exportAll
admin --> bulkOps

admin --> sysReports
admin --> monitorActivity
admin --> auditLogs
admin --> healthCheck
admin --> backup

note right of assignRole
  Permission Required:
  - role_manage

  Can assign:
  - Basic User
  - Department Manager
  - Senior Manager
  - Multiple roles per user

  Validation:
  - User must be approved
  - Department match
end note

note right of cancelAny
  Permission Required:
  - receipt_view_all

  Abilities:
  - Cancel across departments
  - No approval needed
  - Override any status
  - Full audit trail

  Use cases:
  - Emergency corrections
  - System cleanup
  - Compliance issues
end note

note bottom of auditLogs
  Audit Log Contents:
  - All user actions
  - Permission changes
  - Receipt modifications
  - Approval decisions
  - System configurations

  Retention: Permanent
  Access: Admin only
end note

@enduml
```

---

## 6. Public User Use Cases

```plantuml
@startuml
!theme plain
title Public Receipt Verification Use Cases

actor "Public User" as public

rectangle "QR Code Verification" {
  usecase "Scan QR Code" as scan
  usecase "Enter Receipt Number" as enter
  usecase "Verify Receipt" as verify
  usecase "View Receipt Details" as viewDetails
  usecase "Check Authenticity" as checkAuth
  usecase "Download Verification PDF" as downloadPDF
}

rectangle "Public Information" {
  usecase "View Organization Info" as orgInfo
  usecase "View Department Info" as deptInfo
  usecase "View Receipt Status" as status
}

public --> scan
public --> enter
scan ..> verify: <<include>>
enter ..> verify: <<include>>

verify --> viewDetails
viewDetails ..> checkAuth: <<include>>
viewDetails ..> downloadPDF: <<extend>>

public --> orgInfo
public --> deptInfo
public --> status

note right of verify
  No Authentication Required

  Access Method:
  1. Scan QR Code
  2. Enter receipt number manually

  URL Pattern:
  /check/{date_part}/{number_part}

  Example:
  /check/021068/0042
end note

note right of viewDetails
  Public Information Shown:
  - Receipt number
  - Issue date
  - Department name
  - Total amount
  - Purpose
  - Status (Active/Cancelled)

  Hidden Information:
  - Recipient personal details
  - Edit/Cancel history
  - Internal notes
end note

note bottom of checkAuth
  Authenticity Checks:
  ✓ Valid receipt number
  ✓ Exists in database
  ✓ Not cancelled
  ✓ Valid QR code
  ✓ Matches organization

  Visual Indicators:
  🟢 Valid & Active
  🔴 Cancelled
  ⚠️ Not Found
end note

@enduml
```

---

## 7. Workflow Use Case Diagram

```plantuml
@startuml
!theme plain
title Complete Workflow Use Cases

left to right direction

actor "Basic User" as basic
actor "Dept Manager" as dept
actor "Senior Manager" as senior
actor "System Admin" as admin

rectangle "Receipt Lifecycle" {

  usecase "UC1: Create Receipt" as uc1
  usecase "UC2: Edit Draft" as uc2
  usecase "UC3: Confirm Receipt" as uc3
  usecase "UC4: Submit Edit Request" as uc4
  usecase "UC5: Approve Edit (Dept)" as uc5
  usecase "UC6: Approve Edit (Senior)" as uc6
  usecase "UC7: Apply Changes" as uc7
  usecase "UC8: Submit Cancel Request" as uc8
  usecase "UC9: Approve Cancel" as uc9
  usecase "UC10: Direct Cancel" as uc10
  usecase "UC11: Generate Audit Log" as uc11
}

' Basic User flow
basic --> uc1
uc1 ..> uc2: <<extend>>\nif draft
uc2 ..> uc3: <<include>>
uc3 ..> uc4: <<extend>>\nif needs edit
basic --> uc8

' Department Manager flow
dept --> uc5
uc4 ..> uc5: <<include>>\nfrom basic user
uc5 ..> uc7: <<include>>
dept --> uc9
uc8 ..> uc9: <<include>>\nfrom basic user
dept --> uc10

' Senior Manager flow
senior --> uc6
uc4 ..> uc6: <<include>>\nfrom dept manager
uc6 ..> uc7: <<include>>
senior --> uc10

' Admin
admin --> uc10: "all departments"

' Audit
uc7 ..> uc11: <<include>>
uc9 ..> uc11: <<include>>
uc10 ..> uc11: <<include>>

note right of uc5
  Department Manager approves:
  - Basic User edit requests
  - Same department only
  - Creates change log
end note

note right of uc6
  Senior Manager approves:
  - Dept Manager edit requests
  - Same department only
  - Higher authority
end note

note bottom of uc11
  All state changes logged:
  - Who made the change
  - What was changed
  - When it occurred
  - Why (reason/approval)
  - Before/after values
end note

@enduml
```

---

## Notes:
- All use cases enforce role-based permissions
- Department scope applies to all approval use cases
- Audit logging is automatic for all state changes
- Public access is read-only and limited

