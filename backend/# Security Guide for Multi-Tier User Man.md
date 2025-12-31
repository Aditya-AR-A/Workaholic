# Security Guide for Multi-Tier User Management System

## 1. Authentication & Authorization

### 1.1 Authentication

- **Token-based Authentication**: We use `rest_framework.authentication.SessionAuthentication` for browser-based access and `BasicAuthentication` for APIs.
- **Future Improvement**: Implement JWT (JSON Web Tokens) for stateless authentication across different clients (Mobile, Web).

### 1.2 Authorization (RBAC)

- **Superadmin**: Has global access. Can manage companies and system-wide settings.
- **Company Admin**: Has access only to their specific company's data. Can manage employees and departments within their company.
- **Employee**: Has restricted access based on their role and department.

## 2. Tenant Isolation

- **Logical Isolation**: All queries must be filtered by `company_id` for non-Superadmin users.
- **Implementation**:
  - `User` model has a `company` foreign key.
  - ViewSets should override `get_queryset()` to filter by `request.user.company`.

## 3. Data Protection

- **Passwords**: Hashed using Django's default PBKDF2 password hasher.
- **PII**: Personally Identifiable Information (email, phone, address) is stored in `User` and `Profile` models.
- **HTTPS**: TLS 1.3 should be enforced in production.

## 4. Audit Logging

- **Action Logging**: Critical actions (creation, deletion, updates) on `User`, `Company`, and `Permission` changes should be logged.
- **Current Implementation**: `updated_by` and `created_by` fields on models provide basic audit trails.

## 5. Security Checklist for Developers

- [ ] Always filter querysets by `request.user.company` for multi-tenant views.
- [ ] Do not expose sensitive fields (like password hashes) in Serializers.
- [ ] Use `IsAuthenticated` permission class by default.
- [ ] Validate file uploads (size and type) in `TicketAttachement` and `Profile`.

---

# Access Control, Roles & Permission Scope

**Architecture & Policy Documentation**

---

## 1. Core Principles (Non-Negotiable)

1. **Company isolation by default**

   - No data crosses company boundaries unless explicitly allowed.
2. **Permissions over roles**

   - Roles are *labels*.
   - Permissions are *authoritative*.
3. **Projects are the primary access boundary**

   - Most real power exists at the project level.
4. **Clients are independent entities**

   - They are not owned by companies.
   - They gain access only through projects.
5. **Explicit > Inherited > Assumed**

   - Nothing is granted implicitly without a clear rule.

---

## 2. Entity Definitions & Scope

### 2.1 User

- Represents a real person.
- Can belong to:

  - Multiple companies
  - Multiple projects
- Can hold **different permissions per project**.

---

### 2.2 Company

- Organizational boundary.
- Owns:

  - Internal users
  - Company-owned projects
  - Company-level permissions
- Does **not** automatically own clients.

---

### 2.3 Client (Independent Entity)

- A user type with **no default company ownership**.
- Access is granted:

  - Per project
  - By the project-owning company
- Can work with:

  - One or many companies
  - Different permissions per project

---

### 2.4 Project

- Primary collaboration and access unit.
- Has:

  - One **owning company**
  - Optional **participating companies**
  - Explicit user permissions
- Defines **what actions are allowed**, independent of company role.

---

## 3. Role Strategy (Revised)

### 3.1 Company Roles (Minimal & Fixed)

Company roles exist **only for governance**, not granular control.

#### Defined Company Roles

- **SuperAdmin**

  - Full access across company and projects
  - Can override any permission
- **Admin**

  - Full company access
  - Can manage users, projects, and permissions
- **Member**

  - No implicit permissions
  - Access strictly defined by permissions

> All non-admin users rely **entirely on permissions**, not roles.

---

### 3.2 Why Minimize Roles?

- Roles become rigid over time
- Permissions scale better
- Easier audits and testing
- Supports edge cases cleanly

---

## 4. Permission-First Access Model

### 4.1 Permission Philosophy

> **Every meaningful action maps to a permission.**

Examples:

- View project data
- Edit project settings
- Assign project permissions
- View financials
- Invite users
- Export data

Permissions are:

- Explicit
- Atomic
- Auditable

---

### 4.2 Permission Scope Separation

Permissions are always scoped to **where they apply**.

---

#### A) Company-Level Permissions

**Purpose:**
Control organizational actions.

Examples:

- Manage company users
- Create projects
- View company-wide reports
- Manage billing

Rules:

- Do **not** grant project access automatically
- Define *who can create or manage projects*, not who can work inside them

---

#### B) Project-Level Permissions

**Purpose:**
Control actual work and data access.

Examples:

- View project
- Edit project data
- Manage project users
- Approve deliverables
- Access sensitive sections

Rules:

- Explicit assignment required
- Overrides company-level assumptions
- User can have **different permissions per project**

---

## 5. Project Access Model (Finalized)

### 5.1 Project Creation

- A project is always created **under a company**.
- Creating company becomes the **owning company**.

---

### 5.2 Project Access Paths

A company may:

1. **Create a project**
2. **Be granted access to an existing project**

Access is always:

- Explicit
- Permission-based
- Auditable

---

### 5.3 Client Access

- Clients do **not** own projects.
- Clients receive:

  - Project-specific permissions
  - No implicit company permissions
- All access is revocable at project level.

---

## 6. Permission Inheritance & Conflict Rules

### 6.1 Inheritance Rules

1. **Project permissions override company permissions**
2. Company role defines:

   - Eligibility
   - Maximum allowed permissions
3. No upward inheritance
   (Project permissions do not elevate company authority)

---

### 6.2 Conflict Resolution Rules

1. **Most restrictive wins**
2. Deny > Allow
3. Explicit > Inherited
4. Project scope > Company scope

These rules are fixed and must not be bypassed.

---

## 7. Auditing & Governance

### 7.1 Audit Requirements

Every change must be logged:

- Permission granted
- Permission revoked
- Scope changed
- Role changed

Audit record must include:

- Who made the change
- When
- Target user
- Scope (company / project)
- Previous state → new state

---

## 8. Scalability & Future Safety

### 8.1 Design Guarantees

- New permissions can be added without migrations
- New project types do not affect company logic
- Multi-company projects are supported without exceptions

---

### 8.2 Explicit Non-Goals

- No implicit access
- No magic roles
- No hard-coded business rules

---

## 9. Testing Expectations (Conceptual)

Test **permission scenarios**, not features:

- Same user, different projects, different permissions
- Client + employee collaboration
- Permission downgrade effects
- Access after revocation
- Cross-company data isolation attempts

---

## 10. Final Summary (TL;DR)

- **Company roles are minimal and administrative**
- **Permissions define real access**
- **Projects are the core access boundary**
- **Clients are independent entities**
- **Users can have different permissions per project**
- **All access is explicit, auditable, and revocable**

---

## One-line Principle (Anchor)

> **Roles define authority ceilings. Permissions define reality.**

---
