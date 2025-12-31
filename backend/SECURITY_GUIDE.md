# Security Guide for Multi-Tier User Management System

## 1. Authentication & Authorization

### 1.1 Authentication

- SessionAuthentication supports browser-based sessions.
- BasicAuthentication supports simple API access.

### 1.2 Authorization

- Superadmin: Global override authority.
- Company admin: Governance authority within a company.
- Member: No implicit access; relies on explicit permissions.

## 2. Tenant Isolation

- Company isolation is the default.
- Cross-company access is only allowed through explicit project participation.

## 3. Access Control Model

### 3.1 Core Principles

- Company isolation by default.
- Permissions are authoritative; roles are labels.
- Projects are the primary access boundary.
- Clients are independent entities; they gain access through projects.
- Explicit assignments are required; no implicit access.

### 3.2 Scope Separation

- Company permissions: Organization governance and administration.
- Project permissions: Work and data access inside a project.

### 3.3 Inheritance & Conflict Rules

- Project scope overrides company scope.
- Explicit deny overrides allow.
- Most restrictive outcome wins.

## 4. Audit Logging

- Permission changes are logged with actor, target, scope, and before/after state.

## 5. Database Entities (Access Control)

- CompanyMembership: User membership and minimal company role.
- Permission: Atomic permission codes with explicit scope.
- CompanyPermissionAssignment: Company-scoped allow/deny assignments.
- ProjectRole: Project role labels owned by a company.
- ProjectRolePermission: Role-to-permission allow/deny mapping.
- ProjectUser: User membership per project, optional role label.
- ProjectPermissionAssignment: Project-scoped allow/deny assignments.
- ProjectCompany: Explicit company participation for multi-company projects.
- PermissionAuditEvent: Audit trail for permission and scope changes.
