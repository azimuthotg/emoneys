# 🔄 UML Sequence Diagrams - E-Money Voucher System

## 1. Edit Request Flow - Basic User

```plantuml
@startuml
!theme plain
title Edit Request Flow - Basic User → Department Manager

actor "Basic User" as user
participant "Receipt" as receipt
participant "EditRequest" as request
participant "Dept Manager" as manager
database "Database" as db

user -> receipt: create receipt (completed)
activate receipt
receipt -> db: save receipt
db --> receipt: receipt saved
receipt --> user: receipt created
deactivate receipt

== Edit Request Phase ==

user -> request: submit edit request
activate request
request -> request: validate user permissions\nhas_permission('receipt_edit_request')
request -> request: generate_request_number()
request -> db: save edit request (status=pending)
db --> request: request saved
request -> user: request created (pending)
deactivate request

== Approval Phase ==

manager -> request: view pending requests
activate request
request -> request: filter by department
request -> manager: show pending requests
deactivate request

manager -> request: approve/reject request
activate request

alt Approve
  request -> request: can_be_approved_by(manager)?
  request -> request: check department match
  request -> request: check permission level
  request -> receipt: apply_changes()
  activate receipt
  receipt -> db: update receipt fields
  receipt -> db: create ReceiptChangeLog
  db --> receipt: changes saved
  receipt --> request: changes applied
  deactivate receipt
  request -> db: update status (applied)
  request -> manager: ✅ request approved
else Reject
  request -> db: update status (rejected)
  request -> db: save rejection_reason
  request -> manager: ❌ request rejected
end

deactivate request

@enduml
```

---

## 2. Edit Request Flow - Department Manager

```plantuml
@startuml
!theme plain
title Edit Request Flow - Department Manager → Senior Manager

actor "Dept Manager" as dept
participant "Receipt" as receipt
participant "EditRequest" as request
participant "Senior Manager" as senior
database "Database" as db

dept -> receipt: create receipt (completed)
activate receipt
receipt -> db: save receipt
receipt --> dept: receipt created
deactivate receipt

== Edit Request Phase ==

dept -> request: submit edit request
activate request
request -> request: validate permissions\nhas_permission('receipt_edit_request')
request -> request: check if user is Dept Manager\nhas_permission('receipt_edit_approve')
request -> request: generate_request_number()
request -> db: save request (status=pending)
request --> dept: request created (pending)
deactivate request

== Senior Manager Approval ==

senior -> request: view pending requests
activate request
request -> request: filter by:\n- same department\n- requester is Dept Manager
request --> senior: show pending requests
deactivate request

senior -> request: approve/reject
activate request

request -> request: can_be_approved_by(senior)?
alt Check Permission
  request -> request: senior.has_permission(\n'receipt_edit_approve_manager')
  request -> request: senior.department ==\nreceipt.department.name
  request -> request: requester.has_permission(\n'receipt_edit_approve') ✅

  alt Approve
    request -> receipt: apply_changes()
    activate receipt
    receipt -> db: update receipt
    receipt -> db: log changes
    receipt --> request: applied
    deactivate receipt
    request -> db: status = applied
    request --> senior: ✅ approved
  else Reject
    request -> db: status = rejected
    request --> senior: ❌ rejected
  end
else Permission Denied
  request --> senior: ❌ cannot approve\n(not same department or\nnot senior manager permission)
end

deactivate request

@enduml
```

---

## 3. Cancel Request Flow - Basic User

```plantuml
@startuml
!theme plain
title Cancel Request Flow - Basic User → Department Manager

actor "Basic User" as user
participant "Receipt" as receipt
participant "CancelRequest" as cancel
participant "Dept Manager" as manager
database "Database" as db

user -> receipt: receipt exists (completed)

== Check Cancel Permission ==

user -> receipt: can_be_cancelled_by(user)?
activate receipt

alt Status is Draft
  receipt -> receipt: status == 'draft'
  receipt -> receipt: created_by == user
  receipt --> user: ✅ can cancel directly
  user -> receipt: cancel(user, reason)
  receipt -> db: status = cancelled
  receipt -> db: log change
  receipt --> user: cancelled
else Status is Completed
  receipt -> receipt: status == 'completed'
  receipt --> user: ❌ cannot cancel directly\nmust submit cancel request
  deactivate receipt

  == Cancel Request Flow ==

  user -> cancel: submit cancel request
  activate cancel
  cancel -> cancel: generate_request_number()
  cancel -> db: save request (pending)
  cancel --> user: request submitted
  deactivate cancel

  == Manager Approval ==

  manager -> cancel: view pending requests
  activate cancel
  cancel -> cancel: filter same department
  cancel --> manager: show requests
  deactivate cancel

  manager -> cancel: approve/reject
  activate cancel

  cancel -> cancel: can_be_approved_by(manager)?
  cancel -> cancel: check department match
  cancel -> cancel: check requester is NOT manager\n!requester.has_permission(\n'receipt_cancel_approve')

  alt Approve
    cancel -> receipt: apply_cancellation()
    activate receipt
    receipt -> db: status = cancelled
    receipt -> db: log cancellation
    receipt --> cancel: cancelled
    deactivate receipt
    cancel -> db: status = applied
    cancel --> manager: ✅ approved
  else Reject
    cancel -> db: status = rejected
    cancel --> manager: ❌ rejected
  end

  deactivate cancel
end

@enduml
```

---

## 4. Cancel Request Flow - Department Manager

```plantuml
@startuml
!theme plain
title Cancel Request Flow - Department Manager (Direct Cancel)

actor "Dept Manager" as dept
participant "Receipt" as receipt
database "Database" as db

dept -> receipt: receipt exists (completed)

== Check Direct Cancel Permission ==

dept -> receipt: can_be_cancelled_directly(user)?
activate receipt

receipt -> receipt: status == 'completed'
receipt -> receipt: user.has_permission(\n'receipt_cancel_department')

alt Has Department Cancel Permission
  receipt --> dept: ✅ can cancel directly
  deactivate receipt

  dept -> receipt: cancel(dept, reason)
  activate receipt
  receipt -> db: status = cancelled
  receipt -> db: cancelled_by = dept
  receipt -> db: cancellation_reason = reason
  receipt -> db: create ReceiptChangeLog
  receipt --> dept: ✅ receipt cancelled
  deactivate receipt
else No Direct Permission
  receipt --> dept: ❌ must submit cancel request
  deactivate receipt

  note right of dept
    Dept Manager can also
    submit cancel request
    to Senior Manager
  end note
end

@enduml
```

---

## 5. Receipt Creation Flow

```plantuml
@startuml
!theme plain
title Receipt Creation Flow

actor User
participant "Receipt Form" as form
participant "Receipt" as receipt
participant "DocumentVolume" as volume
participant "ReceiptItem" as item
database "Database" as db

User -> form: fill receipt details
activate form
form -> form: validate recipient info
form -> form: add receipt items
form -> form: calculate total_amount
form --> User: show preview
deactivate form

User -> receipt: create receipt (draft/completed)
activate receipt

receipt -> receipt: check permission\nhas_permission('receipt_create')

receipt -> volume: get_or_create_volume()
activate volume
volume -> volume: check fiscal year
volume -> volume: increment_document_number()
volume -> db: save last_document_number
volume --> receipt: document_number
deactivate volume

receipt -> receipt: generate_receipt_number()\nformat: ddmmyy/xxxx
receipt -> receipt: generate_qr_code()
receipt -> db: save receipt

loop for each item
  receipt -> item: create ReceiptItem
  activate item
  item -> db: save item
  item --> receipt: item created
  deactivate item
end

receipt -> db: create ReceiptChangeLog\naction='created'

alt Status is Completed
  receipt -> db: status = 'completed'
  receipt --> User: ✅ receipt created (completed)\ncannot edit directly
else Status is Draft
  receipt -> db: status = 'draft'
  receipt --> User: ✅ receipt created (draft)\ncan edit directly
end

deactivate receipt

@enduml
```

---

## 6. Permission Check Flow

```plantuml
@startuml
!theme plain
title Permission Check Flow

actor User
participant "View/Action" as view
participant "User Model" as user
participant "UserRole" as userrole
participant "Role" as role
participant "Permission" as perm

view -> user: has_permission('receipt_edit_approve')
activate user

alt Is Superuser or Staff
  user -> user: is_superuser == True\nor is_staff == True
  user --> view: ✅ True (bypass)
else Check Role Permissions
  user -> userrole: get_roles()
  activate userrole
  userrole -> userrole: filter(user=user, is_active=True)
  userrole --> user: user_roles
  deactivate userrole

  loop for each role
    user -> role: has_permission('receipt_edit_approve')
    activate role
    role -> perm: filter(name='receipt_edit_approve',\nis_active=True).exists()
    activate perm

    alt Permission Exists
      perm --> role: ✅ True
      role --> user: ✅ True
      user --> view: ✅ True (permission granted)
    else Permission Not Found
      perm --> role: ❌ False
      role --> user: ❌ False
      deactivate perm
      deactivate role
    end
  end

  user --> view: ❌ False (no permission)
end

deactivate user

@enduml
```

---

## 7. Department Scope Validation

```plantuml
@startuml
!theme plain
title Department Scope Validation Flow

actor "Manager" as mgr
participant "Request" as req
participant "Receipt" as receipt
participant "Permission Check" as check
database "Database" as db

mgr -> req: attempt to approve request
activate req

req -> check: can_be_approved_by(mgr)?
activate check

== Check 1: Department Match ==
check -> receipt: get receipt.department.name
activate receipt
receipt --> check: department_name
deactivate receipt

check -> mgr: get mgr.department
mgr --> check: user_department

alt Department Match
  check -> check: user_department ==\nreceipt.department.name ✅

  == Check 2: Permission Level ==
  check -> mgr: has_permission(\n'receipt_edit_approve_manager')

  alt Senior Manager Permission
    mgr --> check: ✅ True
    check -> req: get requested_by
    req --> check: requester
    check -> check: requester.has_permission(\n'receipt_edit_approve')

    alt Requester is Dept Manager
      check --> req: ✅ can approve
      req -> db: process approval
      req --> mgr: ✅ approved
    else Requester is Basic User
      check --> req: ❌ cannot approve\n(wrong permission level)
      req --> mgr: ❌ denied
    end

  else Dept Manager Permission
    mgr --> check: has_permission(\n'receipt_edit_approve')
    check -> check: requester is Basic User?\n!has_permission('receipt_edit_approve')

    alt Requester is Basic User
      check --> req: ✅ can approve
      req -> db: process approval
      req --> mgr: ✅ approved
    else Requester is Manager
      check --> req: ❌ cannot approve\n(same permission level)
      req --> mgr: ❌ denied
    end
  end

else Department Mismatch
  check --> req: ❌ cannot approve\n(different department)
  deactivate check
  req --> mgr: ❌ access denied
end

deactivate req

@enduml
```

---

## Notes:
- All flows enforce department scope rules
- Permission checks cascade from Superuser → Role → Permission
- Approval hierarchy is strictly enforced
- Audit logs are created for all state changes

