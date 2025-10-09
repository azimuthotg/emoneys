# 📐 UML Class Diagram - E-Money Voucher System

## 1. Core Models Class Diagram

```plantuml
@startuml
!theme plain

' ========== USER & AUTHENTICATION ==========
class User {
  + ldap_uid: String(13)
  + npu_staff_id: String(20)
  + full_name: String(255)
  + department: String(255)
  + position_title: String(255)
  + is_superuser: Boolean
  + is_staff: Boolean
  --
  + get_roles(): QuerySet<Role>
  + has_role(role_name): Boolean
  + has_permission(permission_name): Boolean
  + assign_role(role, assigned_by)
}

class Permission {
  + name: String(50) <<unique>>
  + description: Text
  + is_active: Boolean
  --
  PERMISSION_TYPES:
  - receipt_create
  - receipt_view_own
  - receipt_edit_request
  - receipt_edit_approve
  - receipt_edit_approve_manager
  - receipt_cancel_approve
  - receipt_cancel_approve_manager
  - receipt_cancel_department
  - receipt_view_department
  - receipt_view_all
}

class Role {
  + name: String(50) <<unique>>
  + display_name: String(100)
  + description: Text
  + department_scope: String(255)
  + is_active: Boolean
  --
  + has_permission(permission_name): Boolean
  --
  ROLE_TYPES:
  - admin (System Admin)
  - senior_manager (Senior Manager)
  - department_manager (Dept Manager)
  - basic_user (Basic User)
}

class UserRole {
  + is_active: Boolean
  + assigned_at: DateTime
  --
  <<unique_together>>
  (user, role)
}

User "1" -- "*" UserRole
Role "1" -- "*" UserRole
Role "*" -- "*" Permission

' ========== DEPARTMENT & DOCUMENT VOLUME ==========
class Department {
  + name: String(255) <<unique>>
  + code: String(10) <<unique>>
  + address: Text
  + postal_code: String(10)
  + phone: String(20)
  + is_active: Boolean
  --
  + get_current_volume(): DocumentVolume
  + get_receipt_count(): Integer
}

class DocumentVolume {
  + fiscal_year: Integer
  + volume_code: String(10) <<unique>>
  + status: String(20)
  + last_document_number: Integer
  + max_documents: Integer
  + fiscal_year_start: Date
  + fiscal_year_end: Date
  --
  + get_next_document_number(): Integer
  + increment_document_number(): Integer
  --
  STATUS_CHOICES:
  - active
  - closed
  - archived
}

Department "1" -- "*" DocumentVolume
User "1" -- "*" DocumentVolume: created_by

' ========== RECEIPT SYSTEM ==========
class Receipt {
  + receipt_number: String(15) <<unique>>
  + recipient_name: String(255)
  + recipient_address: Text
  + recipient_id_card: String(20)
  + purpose: Text
  + total_amount: Decimal(10,2)
  + status: String(20)
  + qr_code_url: String(500)
  --
  + calculate_total(): Decimal
  + generate_receipt_number(): String
  + generate_qr_code(): String
  + can_be_cancelled_by(user): Boolean
  + can_be_cancelled_directly(user): Boolean
  + cancel(user, reason): Boolean
  --
  STATUS_CHOICES:
  - draft
  - completed
  - cancelled
}

class ReceiptItem {
  + description: String(500)
  + amount: Decimal(10,2)
  + order: Integer
}

class ReceiptTemplate {
  + name: String(255)
  + max_amount: Decimal(10,2)
  + fixed_amount: Decimal(10,2)
  + is_active: Boolean
  + category: String(100)
}

Department "1" -- "*" Receipt
User "1" -- "*" Receipt: created_by
Receipt "1" -- "*" ReceiptItem
ReceiptTemplate "0..1" -- "*" ReceiptItem

' ========== EDIT REQUEST SYSTEM ==========
class ReceiptEditRequest {
  + request_number: String(20) <<unique>>
  + reason: Text
  + status: String(20)
  + new_recipient_name: String(255)
  + new_recipient_address: Text
  + new_purpose: Text
  + rejection_reason: Text
  --
  + generate_request_number(): String
  + can_be_approved_by(user): Boolean
  + approve(approver): Boolean
  + reject(approver, reason): Boolean
  + apply_changes(): Boolean
  --
  STATUS_CHOICES:
  - pending
  - approved
  - rejected
  - withdrawn
  - applied
}

class ReceiptEditRequestItem {
  + action: String(10)
  + new_description: String(500)
  + new_amount: Decimal(10,2)
  + new_order: Integer
  --
  ACTION_CHOICES:
  - update
  - add
  - delete
}

Receipt "1" -- "*" ReceiptEditRequest
User "1" -- "*" ReceiptEditRequest: requested_by
User "0..1" -- "*" ReceiptEditRequest: approved_by
ReceiptEditRequest "1" -- "*" ReceiptEditRequestItem
ReceiptItem "0..1" -- "0..1" ReceiptEditRequestItem: original_item

' ========== CANCEL REQUEST SYSTEM ==========
class ReceiptCancelRequest {
  + request_number: String(20) <<unique>>
  + cancel_reason: Text
  + status: String(20)
  + rejection_reason: Text
  --
  + generate_request_number(): String
  + can_be_approved_by(user): Boolean
  + approve(approver): Boolean
  + reject(approver, reason): Boolean
  + apply_cancellation(): Boolean
  --
  STATUS_CHOICES:
  - pending
  - approved
  - rejected
  - withdrawn
  - applied
}

Receipt "1" -- "*" ReceiptCancelRequest
User "1" -- "*" ReceiptCancelRequest: requested_by
User "0..1" -- "*" ReceiptCancelRequest: approved_by

' ========== AUDIT LOG ==========
class ReceiptChangeLog {
  + action: String(20)
  + field_name: String(100)
  + old_value: Text
  + new_value: Text
  + notes: Text
  + changed_at: DateTime
  --
  ACTION_CHOICES:
  - created
  - updated
  - cancelled
  - edit_requested
  - edit_approved
  - edit_rejected
  - edit_applied
}

Receipt "1" -- "*" ReceiptChangeLog
ReceiptEditRequest "0..1" -- "*" ReceiptChangeLog
User "1" -- "*" ReceiptChangeLog: changed_by

' ========== USER ACTIVITY LOG ==========
class UserActivityLog {
  + action: String(100)
  + ip_address: String(45)
  + user_agent: Text
  + timestamp: DateTime
  + details: JSONField
}

User "1" -- "*" UserActivityLog

@enduml
```

---

## 2. Role & Permission Relationship

```plantuml
@startuml
!theme plain

package "Role System" {

  class "System Admin" as Admin {
    Permissions:
    ✅ receipt_view_all
    ✅ receipt_export
    ✅ user_manage
    ✅ role_manage
    ✅ system_config
    ✅ report_view
  }

  class "Senior Manager" as Senior {
    Permissions:
    ✅ receipt_create
    ✅ receipt_view_own
    ✅ receipt_view_department
    ✅ receipt_edit_request
    ✅ receipt_edit_approve
    ✅ receipt_edit_approve_manager ⭐
    ✅ receipt_cancel_request
    ✅ receipt_cancel_approve
    ✅ receipt_cancel_approve_manager ⭐
    ✅ receipt_cancel_department
    ✅ report_view
  }

  class "Department Manager" as DeptMgr {
    Permissions:
    ✅ receipt_create
    ✅ receipt_view_own
    ✅ receipt_view_department
    ✅ receipt_edit_request
    ✅ receipt_edit_approve ⭐
    ✅ receipt_cancel_request
    ✅ receipt_cancel_approve ⭐
    ✅ receipt_cancel_department
  }

  class "Basic User" as Basic {
    Permissions:
    ✅ receipt_create
    ✅ receipt_view_own
    ✅ receipt_edit_request
    ✅ receipt_edit_request_view
    ✅ receipt_edit_withdraw
    ✅ receipt_cancel_request
    ✅ receipt_cancel_request_view
    ✅ receipt_cancel_withdraw
  }
}

Admin -down-> Senior: manages
Senior -down-> DeptMgr: approves requests from
DeptMgr -down-> Basic: approves requests from

note right of Senior
  ⭐ Key Permissions:
  - Approves Dept Manager edit requests
  - Approves Dept Manager cancel requests
  - Can cancel receipts directly
end note

note right of DeptMgr
  ⭐ Key Permissions:
  - Approves Basic User edit requests
  - Approves Basic User cancel requests
  - Can cancel receipts directly
end note

@enduml
```

---

## 3. Permission Inheritance Diagram

```plantuml
@startuml
!theme plain

skinparam packageStyle rectangle

package "Permission Hierarchy" {

  rectangle "System Level" #LightBlue {
    (receipt_view_all)
    (user_manage)
    (role_manage)
    (system_config)
    (receipt_export)
  }

  rectangle "Senior Manager Level" #LightGreen {
    (receipt_edit_approve_manager)
    (receipt_cancel_approve_manager)
  }

  rectangle "Department Level" #LightYellow {
    (receipt_view_department)
    (receipt_edit_approve)
    (receipt_cancel_approve)
    (receipt_cancel_department)
  }

  rectangle "User Level" #LightCoral {
    (receipt_create)
    (receipt_view_own)
    (receipt_edit_request)
    (receipt_cancel_request)
  }
}

actor "Admin" as admin
actor "Senior Manager" as senior
actor "Dept Manager" as dept
actor "Basic User" as basic

admin --> "System Level"
admin --> "Senior Manager Level"
admin --> "Department Level"
admin --> "User Level"

senior --> "Senior Manager Level"
senior --> "Department Level"
senior --> "User Level"

dept --> "Department Level"
dept --> "User Level"

basic --> "User Level"

@enduml
```

---

## 4. Department Scope Diagram

```plantuml
@startuml
!theme plain

package "Department A" {
  actor "Senior A" as sa
  actor "Dept Mgr A" as dma
  actor "Basic A" as ba

  sa -down-> dma: approves
  dma -down-> ba: approves
}

package "Department B" {
  actor "Senior B" as sb
  actor "Dept Mgr B" as dmb
  actor "Basic B" as bb

  sb -down-> dmb: approves
  dmb -down-> bb: approves
}

actor "System Admin" as admin

admin -down-> sa: manages all
admin -down-> sb: manages all

note right of admin
  Can access ALL departments
  No scope restrictions
end note

note bottom of sa
  ❌ CANNOT approve requests from Dept B
  ✅ CAN approve requests from Dept A only

  Scope Rule:
  user.department == receipt.department.name
end note

@enduml
```

---

## Notes:
- ⭐ = Key distinguishing permissions
- All relationships follow department scope rules (except Admin)
- Approval flow is strictly hierarchical within same department
- Cross-department access is Admin-only

