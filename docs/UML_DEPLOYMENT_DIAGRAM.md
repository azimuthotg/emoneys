# 🏗️ UML Deployment & Component Diagrams - E-Money Voucher System

## 1. Deployment Diagram

```plantuml
@startuml
!theme plain
title E-Money Voucher System - Deployment Diagram

node "Client Devices" {
  node "Web Browser" as browser {
    component "HTML/CSS/JavaScript" as frontend
    component "Bootstrap 5" as bootstrap
    component "jQuery/AJAX" as ajax
  }

  node "Mobile Browser" as mobile {
    component "Responsive UI" as responsive
    component "QR Scanner" as qr
  }
}

node "Application Server" as appserver {
  node "Django Application" as django {
    component "Views Layer" as views
    component "Models Layer" as models
    component "URL Router" as urls
    component "Template Engine" as templates
    component "Authentication" as auth
  }

  node "Background Tasks" as tasks {
    component "PDF Generator" as pdf
    component "QR Code Generator" as qrgen
    component "Email Service" as email
  }
}

node "Database Server" as dbserver {
  database "SQLite / MySQL\n(Production)" as db {
    storage "User Tables" as user_tables
    storage "Receipt Tables" as receipt_tables
    storage "Request Tables" as request_tables
    storage "Audit Tables" as audit_tables
  }
}

node "File Storage" as storage {
  folder "Static Files" as static {
    file "CSS/JS/Images" as assets
  }

  folder "Media Files" as media {
    file "PDF Documents" as pdfs
    file "QR Codes" as qrcodes
  }

  folder "Font Files" as fonts {
    file "THSarabunNew" as thai_fonts
  }
}

node "External Services" as external {
  node "NPU AD Server" as npu {
    component "LDAP/AD API" as ldap
    component "User Directory" as directory
  }

  node "Email Server" as smtp {
    component "SMTP Service" as smtp_svc
  }
}

' Connections
browser --> django : HTTPS
mobile --> django : HTTPS
django --> db : ORM Queries
django --> npu : Authentication
django --> storage : Read/Write
django --> smtp : Send Emails
tasks --> storage : Generate Files
pdf --> fonts : Load Thai Fonts

note right of django
  Server: Django 4.2.24
  WSGI: Gunicorn (Production)
  Development: runserver
  Port: 8002 (Dev), 80/443 (Prod)
end note

note right of db
  Development: SQLite
  Production: MySQL 8.0+
  Migrations: Django ORM
  Backup: Daily automated
end note

note bottom of npu
  NPU AD Integration:
  - Primary authentication
  - User data sync
  - Fallback: File-based auth
end note

@enduml
```

---

## 2. Component Diagram - System Architecture

```plantuml
@startuml
!theme plain
title E-Money Voucher System - Component Architecture

package "Presentation Layer" {
  component "Templates" as tmpl {
    portin "Render" as render_in
    portout "HTML" as html_out
  }

  component "Static Assets" as static {
    portout "CSS/JS" as assets_out
  }

  component "Forms" as forms {
    portin "User Input" as form_in
    portout "Validated Data" as form_out
  }
}

package "Application Layer" {
  component "Views" as views {
    portin "HTTP Request" as req_in
    portout "HTTP Response" as resp_out
  }

  component "Authentication" as auth {
    portin "Credentials" as cred_in
    portout "User Session" as session_out
  }

  component "Permission System" as perms {
    portin "Permission Check" as perm_in
    portout "Access Decision" as perm_out
  }

  component "Business Logic" as logic {
    portin "Action" as action_in
    portout "Result" as result_out
  }
}

package "Data Layer" {
  component "Models" as models {
    portin "ORM Operations" as orm_in
    portout "Model Instances" as inst_out
  }

  component "Database" as db {
    portin "SQL Queries" as sql_in
    portout "Result Sets" as sql_out
  }

  component "Migrations" as migrations {
    portout "Schema Updates" as schema_out
  }
}

package "Service Layer" {
  component "PDF Generator" as pdf {
    portin "Receipt Data" as pdf_in
    portout "PDF File" as pdf_out
  }

  component "QR Generator" as qr {
    portin "Receipt Number" as qr_in
    portout "QR Image" as qr_out
  }

  component "NPU API Client" as npu {
    portin "Auth Request" as npu_in
    portout "User Data" as npu_out
  }

  component "Report Generator" as reports {
    portin "Query Params" as report_in
    portout "Report File" as report_out
  }
}

package "Utility Layer" {
  component "Fiscal Year Utils" as fiscal {
    portout "FY Data" as fy_out
  }

  component "Number Converter" as numconv {
    portin "Number" as num_in
    portout "Thai Text" as thai_out
  }

  component "Audit Logger" as audit {
    portin "Event" as event_in
    portout "Log Entry" as log_out
  }
}

' Connections
req_in --> views
views --> auth : authenticate
views --> perms : check permission
views --> forms : validate
views --> logic : execute
logic --> models : CRUD
models --> db : query
pdf --> models : get data
qr --> models : get receipt
views --> pdf : generate
views --> qr : create QR
views --> tmpl : render
tmpl --> html_out
auth --> npu : external auth
logic --> audit : log event
migrations --> db : update schema

note right of views
  Main Views:
  - receipt_create_view
  - receipt_list_view
  - receipt_detail_view
  - edit_request_view
  - cancel_request_view
  - approval_views
end note

note right of models
  Core Models:
  - User, Role, Permission
  - Receipt, ReceiptItem
  - ReceiptEditRequest
  - ReceiptCancelRequest
  - ReceiptChangeLog
end note

note bottom of pdf
  PDF Generator:
  - ReportLab library
  - THSarabunNew fonts
  - Organization template
  - QR code embedding
end note

@enduml
```

---

## 3. Component Diagram - Receipt System

```plantuml
@startuml
!theme plain
title Receipt Management Component Diagram

package "Receipt Components" {

  component "Receipt Controller" as ctrl {
    portin "User Request" as req
    portout "Response" as resp
  }

  component "Receipt Service" as svc {
    portin "Action" as action
    portout "Result" as result
  }

  component "Receipt Repository" as repo {
    portin "Data Operation" as data_op
    portout "Receipt Data" as data
  }

  component "Validation Service" as validation {
    portin "Receipt Data" as val_in
    portout "Validation Result" as val_out
  }

  component "Number Generator" as numgen {
    portin "Date + Sequence" as gen_in
    portout "Receipt Number" as gen_out
  }
}

package "Request Management" {

  component "Edit Request Handler" as edit_handler {
    portin "Edit Request" as edit_req
    portout "Edit Response" as edit_resp
  }

  component "Cancel Request Handler" as cancel_handler {
    portin "Cancel Request" as cancel_req
    portout "Cancel Response" as cancel_resp
  }

  component "Approval Engine" as approval {
    portin "Approval Decision" as approval_in
    portout "Approval Result" as approval_out
  }
}

package "Supporting Services" {

  component "PDF Service" as pdf {
    portin "Receipt" as pdf_receipt
    portout "PDF Document" as pdf_doc
  }

  component "QR Service" as qr {
    portin "Receipt Number" as qr_num
    portout "QR Code" as qr_code
  }

  component "Audit Service" as audit {
    portin "Change Event" as audit_event
    portout "Log Entry" as audit_log
  }

  component "Notification Service" as notify {
    portin "Event" as notify_event
    portout "Notification" as notification
  }
}

' Connections
req --> ctrl
ctrl --> svc
svc --> repo
svc --> validation
svc --> numgen
svc --> edit_handler
svc --> cancel_handler
edit_handler --> approval
cancel_handler --> approval
svc --> pdf
svc --> qr
svc --> audit
approval --> notify
ctrl --> resp

note right of ctrl
  Controllers handle:
  - HTTP requests
  - User input
  - Response formatting
  - Error handling
end note

note right of approval
  Approval Rules:
  - Department scope check
  - Permission validation
  - Role hierarchy enforcement
  - Status validation
end note

note bottom of audit
  Audit captures:
  - All CRUD operations
  - Approval decisions
  - State changes
  - User actions
end note

@enduml
```

---

## 4. Component Diagram - Permission System

```plantuml
@startuml
!theme plain
title Permission System Component Diagram

package "Permission Components" {

  component "Permission Manager" as mgr {
    portin "Permission Check" as check_in
    portout "Access Decision" as decision_out
  }

  component "Role Service" as role_svc {
    portin "Role Query" as role_in
    portout "Role Data" as role_out
  }

  component "Permission Repository" as perm_repo {
    portin "Permission Query" as perm_in
    portout "Permission List" as perm_out
  }

  component "User Role Repository" as user_role_repo {
    portin "User ID" as user_in
    portout "User Roles" as roles_out
  }
}

package "Validation Components" {

  component "Scope Validator" as scope {
    portin "User + Resource" as scope_in
    portout "Scope Valid" as scope_out
  }

  component "Hierarchy Validator" as hierarchy {
    portin "User + Action" as hier_in
    portout "Hierarchy Valid" as hier_out
  }

  component "Department Validator" as dept {
    portin "User + Department" as dept_in
    portout "Department Match" as dept_out
  }
}

component "Permission Cache" as cache {
  portin "Cache Query" as cache_in
  portout "Cached Permissions" as cache_out
}

database "Permission Data" as db {
  storage "Permissions" as perms_table
  storage "Roles" as roles_table
  storage "UserRoles" as user_roles_table
}

' Connections
check_in --> mgr
mgr --> cache : check cache
mgr --> user_role_repo : get user roles
user_role_repo --> db
mgr --> role_svc : get role permissions
role_svc --> perm_repo
perm_repo --> db
mgr --> scope : validate scope
mgr --> hierarchy : validate hierarchy
mgr --> dept : validate department
mgr --> decision_out

cache --> db : cache miss

note right of mgr
  Permission Check Flow:
  1. Check superuser bypass
  2. Check cache
  3. Get user roles
  4. Get role permissions
  5. Validate scope
  6. Return decision
end note

note right of scope
  Scope Validation:
  - Own resources only (Basic)
  - Department resources (Manager)
  - All resources (Admin)
end note

note bottom of hierarchy
  Hierarchy Rules:
  Admin > Senior > Dept Manager > Basic

  Approval:
  - Senior approves Dept Manager
  - Dept Manager approves Basic
  - Same department only
end note

@enduml
```

---

## 5. Network Topology Diagram

```plantuml
@startuml
!theme plain
title Network Topology - Production Environment

cloud "Internet" as internet {
}

node "Load Balancer" as lb {
  component "Nginx" as nginx
  component "SSL/TLS" as ssl
}

node "Web Server 1" as web1 {
  component "Django App 1" as app1
  component "Gunicorn" as gun1
}

node "Web Server 2" as web2 {
  component "Django App 2" as app2
  component "Gunicorn" as gun2
}

database "Database Cluster" as dbcluster {
  node "Primary DB" as primary {
    database "MySQL Primary" as db1
  }

  node "Replica DB" as replica {
    database "MySQL Replica" as db2
  }
}

node "File Server" as fileserver {
  storage "Static Files" as static
  storage "Media Files" as media
  storage "PDF Storage" as pdfs
}

node "Cache Server" as cache {
  database "Redis" as redis
}

node "External Services" as external {
  cloud "NPU AD Server" as npu
  cloud "Email Server" as smtp
}

node "Monitoring" as monitor {
  component "Logging Service" as logs
  component "Metrics Collector" as metrics
  component "Alert Manager" as alerts
}

' Connections
internet --> lb : HTTPS (443)
lb --> web1 : HTTP (8000)
lb --> web2 : HTTP (8000)
web1 --> dbcluster : Read/Write
web2 --> dbcluster : Read/Write
primary --> replica : Replication
web1 --> fileserver : NFS/S3
web2 --> fileserver : NFS/S3
web1 --> cache : Session/Cache
web2 --> cache : Session/Cache
web1 --> external : API Calls
web2 --> external : API Calls
web1 --> monitor : Logs/Metrics
web2 --> monitor : Logs/Metrics

note right of lb
  Load Balancer:
  - SSL termination
  - Round-robin distribution
  - Health checks
  - DDoS protection
end note

note right of dbcluster
  Database:
  - Primary: Read/Write
  - Replica: Read-only
  - Auto-failover
  - Daily backups
end note

note bottom of cache
  Redis Cache:
  - Session storage
  - Permission cache
  - Query cache
  - Rate limiting
end note

@enduml
```

---

## 6. Database Schema Component

```plantuml
@startuml
!theme plain
title Database Schema Components

package "Core Schema" {

  database "User Management" as user_db {
    table "accounts_user" as users
    table "accounts_role" as roles
    table "accounts_permission" as perms
    table "accounts_userrole" as userroles
  }

  database "Department Data" as dept_db {
    table "accounts_department" as depts
    table "accounts_documentvolume" as volumes
  }

  database "Receipt Data" as receipt_db {
    table "accounts_receipt" as receipts
    table "accounts_receiptitem" as items
    table "accounts_receipttemplate" as templates
  }

  database "Request Data" as request_db {
    table "accounts_receipteditrequest" as edit_reqs
    table "accounts_receipteditrequestitem" as edit_items
    table "accounts_receiptcancelrequest" as cancel_reqs
  }

  database "Audit Data" as audit_db {
    table "accounts_receiptchangelog" as changelog
    table "accounts_useractivitylog" as activity
  }
}

' Relationships
users --> userroles : has
roles --> userroles : assigned_to
roles --> perms : has_many
users --> depts : belongs_to
depts --> volumes : has
users --> receipts : creates
receipts --> items : has_many
receipts --> edit_reqs : has_many
receipts --> cancel_reqs : has_many
receipts --> changelog : has_many
edit_reqs --> edit_items : has_many
users --> activity : logged_by

note right of user_db
  Indexes:
  - ldap_uid (unique)
  - department (btree)
  - is_active (btree)

  Constraints:
  - userrole unique(user, role)
end note

note right of receipt_db
  Indexes:
  - receipt_number (unique)
  - status (btree)
  - created_at (btree)
  - department_id (foreign key)

  Full-text:
  - recipient_name
  - purpose
end note

note bottom of audit_db
  Retention:
  - changelog: Permanent
  - activity: 2 years

  Partitioning:
  - By timestamp (monthly)
end note

@enduml
```

---

## 7. Deployment Pipeline Diagram

```plantuml
@startuml
!theme plain
title CI/CD Deployment Pipeline

(*) --> "Code Commit"

"Code Commit" --> "Run Tests" : Git Push

partition "CI Pipeline" {
  "Run Tests" --> "Unit Tests"
  "Unit Tests" --> "Integration Tests"
  "Integration Tests" --> "Security Scan"
  "Security Scan" --> "Code Quality"
}

if "All Checks Pass?" then
  -->[true] "Build Docker Image"
  --> "Tag Image"
  --> "Push to Registry"
else
  -->[false] "Notify Developer"
  --> (*)
endif

partition "Deployment" {
  "Push to Registry" --> "Deploy to Staging"

  if "Staging Tests Pass?" then
    -->[true] "Manual Approval"

    if "Approved?" then
      -->[true] "Deploy to Production"
      --> "Run Migrations"
      --> "Restart Services"
      --> "Health Check"
    else
      -->[false] "Cancel Deployment"
      --> (*)
    endif
  else
    -->[false] "Rollback Staging"
    --> (*)
  endif
}

if "Health Check OK?" then
  -->[true] "Update Monitoring"
  --> "Notify Team"
  --> (*)
else
  -->[false] "Auto Rollback"
  --> "Restore Previous Version"
  --> "Alert Team"
  --> (*)
endif

note right of "Deploy to Production"
  Blue-Green Deployment:
  1. Deploy to inactive environment
  2. Run smoke tests
  3. Switch traffic
  4. Monitor metrics
  5. Keep old version ready
end note

@enduml
```

---

## Notes:
- Production uses load-balanced deployment
- Database replication for high availability
- Static files served via CDN or file server
- Redis for session and cache management
- All communications encrypted (HTTPS/TLS)

