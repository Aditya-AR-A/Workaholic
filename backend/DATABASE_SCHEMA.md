# Database Schema Notes (Core Access Control)

This document describes the database objects added to support tenant isolation, multi-company projects, and per-project permissions.

## New Tables

### core_companymembership

- Purpose: Allow a user to belong to multiple companies with a minimal company role.
- Key columns: user_id, company_id, role, is_active, created_at, updated_at
- Constraints: UNIQUE(user_id, company_id)
- Indexes: (company_id, user_id), (user_id, company_id)

### core_permission

- Purpose: Store atomic permission codes, separated by scope.
- Key columns: scope, code, description, module, is_active
- Constraints: UNIQUE(scope, code)
- Indexes: (scope, code)

### core_companypermissionassignment

- Purpose: Assign allow/deny permissions at the company scope per user.
- Key columns: company_id, user_id, permission_id, effect, granted_by_id
- Constraints: UNIQUE(company_id, user_id, permission_id), CHECK(effect IN ('ALLOW','DENY'))
- Indexes: (company_id, user_id), (user_id, company_id), (permission_id, effect)

### core_projectrole

- Purpose: Optional role labels (owned by a company) to group project permissions.
- Key columns: company_id, name, description, is_active
- Constraints: UNIQUE(company_id, name)
- Indexes: (company_id, name)

### core_projectrolepermission

- Purpose: Define allow/deny permission sets for a project role.
- Key columns: role_id, permission_id, effect
- Constraints: UNIQUE(role_id, permission_id), CHECK(effect IN ('ALLOW','DENY'))
- Indexes: (permission_id, effect)

### core_projectuser (modified)

- Purpose: Project membership, with optional role label.
- Added column: role_id (nullable FK to core_projectrole)
- Indexes added: (project_id, user_id), (user_id, project_id)

### core_projectpermissionassignment

- Purpose: Assign allow/deny permissions at the project scope per user.
- Key columns: project_id, user_id, permission_id, effect, granted_by_id
- Constraints: UNIQUE(project_id, user_id, permission_id), CHECK(effect IN ('ALLOW','DENY'))
- Indexes: (project_id, user_id), (user_id, project_id), (permission_id, effect)

### core_projectcompany

- Purpose: Explicit project participation for companies (owner vs participant).
- Key columns: project_id, company_id, relationship, is_active, created_by_id
- Constraints: UNIQUE(project_id, company_id), CHECK(relationship IN ('OWNER','PARTICIPANT'))
- Indexes: (company_id, project_id)

### core_permissionauditevent

- Purpose: Audit permission grants/revokes and scope changes.
- Key columns: actor_id, target_user_id, scope, company_id, project_id, event_type, before_state, after_state, created_at
- Indexes: (scope, created_at), (target_user_id, created_at)

## Migration

- Added in [0003_companymembership_companypermissionassignment_and_more.py](file:///c:/Users/HP/Desktop/DjangoPractice/backend/core/migrations/0003_companymembership_companypermissionassignment_and_more.py)
