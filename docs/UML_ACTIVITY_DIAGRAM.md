# 🔄 UML Activity Diagrams - E-Money Voucher System

## 1. Receipt Creation Activity Diagram

```plantuml
@startuml
!theme plain
title Receipt Creation Activity Flow

|User|
start
:Navigate to Create Receipt;
:Fill Recipient Details;
note right
  - Recipient name
  - Address
  - ID card number
  - Postal code
end note

:Add Receipt Items;
note right
  - Select from template OR
  - Enter custom items
  - Set amounts
end note

:Calculate Total Amount;

if (Total > 0?) then (yes)
  :Convert Amount to Thai Text;
  :Preview Receipt;

  if (User Decision?) then (Save as Draft)
    |System|
    :Set status = 'draft';
    :Save to database;
    :Receipt can be edited later;
  else (Confirm & Complete)
    |System|
    :Generate receipt number;
    note right
      Format: ddmmyy/xxxx
      Example: 021068/0042
    end note
    :Generate QR Code;
    :Set status = 'completed';
    :Save to database;
    :Create audit log (created);
    :Receipt locked for editing;
  endif

  |User|
  :View success message;
  :Download PDF;
  stop

else (no)
  :Show error: Total must be > 0;
  stop
endif

@enduml
```

---

## 2. Edit Request Submission & Approval Activity

```plantuml
@startuml
!theme plain
title Edit Request - Complete Workflow

|Basic User|
start
:View receipt list;
:Select completed receipt;

if (Receipt status?) then (draft)
  :Edit directly;
  :Save changes;
  stop
else (completed)
  :Click "Request Edit";

  fork
    :Fill edit reason;
  fork again
    :Modify receipt fields;
  fork again
    :Update/Add/Delete items;
  end fork

  :Submit edit request;
endif

|System|
:Validate user permission\nreceipt_edit_request;

if (Has permission?) then (no)
  :Show error: No permission;
  stop
else (yes)
  :Generate request number;
  :Save request (status=pending);
  :Notify Department Manager;
endif

|Department Manager|
:Receive notification;
:View pending requests;
:Review request details;

if (Decision?) then (Approve)
  |System|
  :Check can_be_approved_by()?;

  if (Same department\nAND Basic User request?) then (yes)
    :Apply changes to receipt;
    fork
      :Update receipt fields;
    fork again
      :Update receipt items;
    fork again
      :Recalculate total;
    fork again
      :Create change log;
    end fork
    :Set request status = applied;
    :Notify requester;

    |Basic User|
    :View approval notification;
    :View updated receipt;
    stop

  else (no)
    :Show error: Cannot approve;
    stop
  endif

else (Reject)
  |System|
  :Set request status = rejected;
  :Save rejection reason;
  :Notify requester;

  |Basic User|
  :View rejection;
  :View reason;
  stop
endif

@enduml
```

---

## 3. Cancel Request Activity Diagram

```plantuml
@startuml
!theme plain
title Cancel Request Workflow

|User|
start
:Select receipt to cancel;

|System|
:Check receipt status;

if (Status?) then (draft)
  :Check ownership;
  if (Owner?) then (yes)
    :Cancel directly;
    :Set status = cancelled;
    :Create audit log;
    stop
  else (no)
    :Show error: Not owner;
    stop
  endif

else (completed)
  :Check user role;

  if (Role?) then (Senior Manager)
    :Check department;
    if (Same department?) then (yes)
      :Cancel directly;
      :Set status = cancelled;
      :Save cancellation reason;
      :Create audit log;
      stop
    else (no)
      :Show error: Different dept;
      stop
    endif

  else if (Department Manager)
    fork
      :Option A: Cancel directly;
      :Save reason;
      :Set status = cancelled;
      :Create audit log;
      stop
    fork again
      :Option B: Submit cancel request;
      :To Senior Manager;
    end fork

  else (Basic User)
    |User|
    :Fill cancellation reason;
    :Submit cancel request;

    |System|
    :Generate request number;
    :Save request (pending);
    :Notify Department Manager;

    |Department Manager|
    :Review cancel request;
    :Check same department;

    if (Decision?) then (Approve)
      :Apply cancellation;
      :Set receipt status = cancelled;
      :Set request status = applied;
      :Create audit log;
      :Notify requester;

      |User|
      :View approval;
      stop

    else (Reject)
      :Set request status = rejected;
      :Save rejection reason;
      :Notify requester;

      |User|
      :View rejection;
      stop
    endif
  endif
endif

@enduml
```

---

## 4. Permission Check Activity Diagram

```plantuml
@startuml
!theme plain
title Permission Validation Activity

|System|
start
:User attempts action;
:Get required permission name;

:Check user.is_superuser;
if (Is superuser?) then (yes)
  :Grant access;
  stop
else (no)
  :Check user.is_staff;
  if (Is staff?) then (yes)
    :Grant access;
    stop
  else (no)
    :Get user roles;

    if (Has roles?) then (no)
      :Deny access;
      stop
    else (yes)
      repeat
        :Get next role;
        :Check role.is_active;

        if (Active?) then (yes)
          :Query role permissions;
          :Filter by permission name;
          :Check is_active;

          if (Permission found?) then (yes)
            :Grant access;
            stop
          else (no)
            :Continue to next role;
          endif
        else (no)
          :Continue to next role;
        endif
      repeat while (More roles?)

      :No permission found;
      :Deny access;
      stop
    endif
  endif
endif

@enduml
```

---

## 5. Department Scope Validation Activity

```plantuml
@startuml
!theme plain
title Department Scope Validation Activity

|System|
start
:Manager attempts approval;
:Get receipt department;
:Get manager department;

if (Departments match?) then (no)
  :Deny: Different department;
  stop
else (yes)
  :Get requester info;
  :Get manager permissions;

  if (Manager has\nsenior permission?) then (yes)
    :Check requester is Dept Manager;
    if (Requester has\ndept permission?) then (yes)
      :Allow approval;
      :Senior approves Dept Manager;
      stop
    else (no)
      :Deny: Wrong requester level;
      stop
    endif

  else if (Manager has\ndept permission?) then (yes)
    :Check requester is Basic User;
    if (Requester is Basic?) then (yes)
      :Allow approval;
      :Dept Manager approves Basic User;
      stop
    else (no)
      :Deny: Wrong requester level;
      stop
    endif

  else (no permission)
    :Deny: No approval permission;
    stop
  endif
endif

@enduml
```

---

## 6. User Registration & Approval Activity

```plantuml
@startuml
!theme plain
title User Registration & Approval Workflow

|New User|
start
:Access login page;
:Enter credentials;

|System|
:Check authentication backend;

fork
  :Try NPU AD authentication;
fork again
  :Try file-based authentication;
end fork

if (Auth successful?) then (no)
  :Show login error;
  stop
else (yes)
  :Get or create user;
  :Sync user data from NPU/file;

  if (User exists?) then (yes)
    if (User approved?) then (yes)
      :Check user roles;
      if (Has roles?) then (yes)
        :Allow login;
        :Redirect to dashboard;
        stop
      else (no)
        :Show: No role assigned;
        :Limited access;
        stop
      endif
    else (no)
      :Show: Pending approval;
      stop
    endif

  else (new user)
    :Create user account;
    :Set status = pending;
    :Notify admin;
    :Show: Wait for approval;

    |Admin|
    :Review new user;
    :Check user details;
    :Verify department;

    if (Decision?) then (Approve)
      :Set user.is_active = True;
      :Assign default role;

      if (is_document_staff?) then (yes)
        :Assign Department Manager role;
      else (no)
        :Assign Basic User role;
      endif

      :Notify user;

      |New User|
      :Receive approval email;
      :Login to system;
      :Access dashboard;
      stop

    else (Reject)
      :Set status = rejected;
      :Save rejection reason;
      :Notify user;

      |New User|
      :Receive rejection;
      :Cannot access system;
      stop
    endif
  endif
endif

@enduml
```

---

## 7. Report Generation Activity

```plantuml
@startuml
!theme plain
title Report Generation Activity

|User|
start
:Navigate to Reports;
:Select report type;

fork
  :Set date range;
fork again
  :Select department;
fork again
  :Choose status filter;
fork again
  :Select export format;
end fork

|System|
:Validate user permission\nreport_view;

if (Has permission?) then (no)
  :Show error: No permission;
  stop
else (yes)
  :Apply department scope;

  if (User role?) then (Basic User)
    :Filter: Own receipts only;
  else if (Dept Manager)
    :Filter: Department receipts;
  else if (Senior Manager)
    :Filter: Department receipts;
  else (Admin)
    :No filter: All receipts;
  endif

  :Build query;
  fork
    :Apply date filter;
  fork again
    :Apply department filter;
  fork again
    :Apply status filter;
  end fork

  :Execute query;
  :Aggregate data;

  fork
    :Calculate totals;
  fork again
    :Count receipts;
  fork again
    :Group by status;
  fork again
    :Calculate averages;
  end fork

  if (Export format?) then (Excel)
    :Generate Excel file;
    :Apply organization template;
    :Add charts;
    :Download file;
  else if (PDF)
    :Generate PDF report;
    :Add Thai fonts;
    :Apply branding;
    :Download PDF;
  else (Screen)
    :Render HTML report;
    :Show charts;
    :Enable interactions;
  endif

  |User|
  :View/Download report;
  stop
endif

@enduml
```

---

## 8. Audit Log Activity

```plantuml
@startuml
!theme plain
title Audit Logging Activity

|User|
start
:Perform action on receipt;

|System|
:Capture action details;

fork
  :Get user info;
  :Get IP address;
  :Get timestamp;
fork again
  :Get receipt info;
  :Get old values;
  :Get new values;
fork again
  :Get action type;
  :Get reason/notes;
end fork

:Determine log type;

if (Action type?) then (Create)
  :Log: Receipt created;
  :Save creator;
  :Save initial values;

else if (Update)
  :Log: Receipt updated;
  :Compare old vs new;
  :Save changes;

else if (Edit Request)
  :Log: Edit requested;
  :Save request details;
  :Save requester;

else if (Approval)
  :Log: Request approved;
  :Save approver;
  :Save decision;

else if (Rejection)
  :Log: Request rejected;
  :Save reason;
  :Save rejector;

else if (Cancel)
  :Log: Receipt cancelled;
  :Save canceller;
  :Save reason;

else (Other)
  :Log: Generic action;
  :Save details;
endif

:Create ReceiptChangeLog entry;
:Save to database;

partition "Parallel Logging" {
  fork
    :Create UserActivityLog;
  fork again
    if (Admin viewing?) then (yes)
      :Update audit dashboard;
    endif
  end fork
}

:Return to action flow;
stop

@enduml
```

---

## Notes:
- All activities include permission checks
- Department scope is enforced at every step
- Audit logging happens automatically
- State transitions are atomic transactions
- Error handling returns to appropriate point

