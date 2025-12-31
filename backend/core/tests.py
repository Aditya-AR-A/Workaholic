from django.db import IntegrityError
from django.db import transaction
from django.test import TestCase
from .models import (
    User,
    Company,
    Client,
    Project,
    CompanyMembership,
    Permission,
    CompanyPermissionAssignment,
    ProjectRole,
    ProjectRolePermission,
    ProjectUser,
    ProjectPermissionAssignment,
    ProjectCompany,
)

class UserTestCase(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(email='test@example.com', username='test', password='password')
        self.assertEqual(user.email, 'test@example.com')

class AccessControlSchemaTestCase(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(
            name='Company A',
            email='a@company.com',
            phone='123',
            domain='a.example',
        )
        self.company_b = Company.objects.create(
            name='Company B',
            email='b@company.com',
            phone='456',
            domain='b.example',
        )
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='password',
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='password',
            is_admin=True,
        )

        self.client = Client.objects.create(
            name='Independent Client',
            email='client@example.com',
            phone='999',
            attached_to_company=None,
        )

        self.project_a = Project.objects.create(
            name='Project A',
            description='A',
            client=self.client,
            attached_to_company=self.company_a,
        )
        self.project_b = Project.objects.create(
            name='Project B',
            description='B',
            client=self.client,
            attached_to_company=self.company_b,
        )

    def test_user_can_have_multiple_company_memberships(self):
        CompanyMembership.objects.create(user=self.user, company=self.company_a, role=CompanyMembership.ROLE_MEMBER)
        CompanyMembership.objects.create(user=self.user, company=self.company_b, role=CompanyMembership.ROLE_ADMIN)

        self.assertEqual(self.user.company_memberships.count(), 2)

    def test_company_membership_is_unique_per_user_and_company(self):
        CompanyMembership.objects.create(user=self.user, company=self.company_a, role=CompanyMembership.ROLE_MEMBER)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                CompanyMembership.objects.create(user=self.user, company=self.company_a, role=CompanyMembership.ROLE_ADMIN)

    def test_client_is_independent_and_allows_null_company(self):
        self.assertIsNone(self.client.attached_to_company)

    def test_user_can_have_different_roles_in_different_projects(self):
        role_lead = ProjectRole.objects.create(company=self.company_a, name='Lead', description='Lead')
        role_viewer = ProjectRole.objects.create(company=self.company_b, name='Viewer', description='Viewer')

        ProjectUser.objects.create(project=self.project_a, user=self.user, role=role_lead)
        ProjectUser.objects.create(project=self.project_b, user=self.user, role=role_viewer)

        role_a = ProjectUser.objects.get(project=self.project_a, user=self.user).role.name
        role_b = ProjectUser.objects.get(project=self.project_b, user=self.user).role.name

        self.assertNotEqual(role_a, role_b)

    def test_permission_scope_unique(self):
        Permission.objects.create(scope=Permission.SCOPE_PROJECT, code='project.view', description='View project')
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Permission.objects.create(scope=Permission.SCOPE_PROJECT, code='project.view', description='Duplicate')

    def test_company_permission_assignment_constraints(self):
        perm = Permission.objects.create(scope=Permission.SCOPE_COMPANY, code='company.users.manage', description='Manage users')
        CompanyPermissionAssignment.objects.create(company=self.company_a, user=self.user, permission=perm, effect='ALLOW', granted_by=self.admin)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                CompanyPermissionAssignment.objects.create(company=self.company_a, user=self.user, permission=perm, effect='ALLOW', granted_by=self.admin)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                CompanyPermissionAssignment.objects.create(company=self.company_a, user=self.admin, permission=perm, effect='BAD')

    def test_project_permission_assignment_constraints(self):
        perm = Permission.objects.create(scope=Permission.SCOPE_PROJECT, code='project.ticket.edit', description='Edit ticket')
        ProjectPermissionAssignment.objects.create(project=self.project_a, user=self.user, permission=perm, effect='DENY', granted_by=self.admin)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                ProjectPermissionAssignment.objects.create(project=self.project_a, user=self.user, permission=perm, effect='DENY', granted_by=self.admin)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                ProjectPermissionAssignment.objects.create(project=self.project_a, user=self.admin, permission=perm, effect='NOPE')

    def test_project_company_participation_constraints(self):
        ProjectCompany.objects.create(project=self.project_a, company=self.company_a, relationship='OWNER', created_by=self.admin)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                ProjectCompany.objects.create(project=self.project_a, company=self.company_a, relationship='OWNER', created_by=self.admin)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                ProjectCompany.objects.create(project=self.project_a, company=self.company_b, relationship='INVALID', created_by=self.admin)

    def test_project_role_permission_constraints(self):
        perm = Permission.objects.create(scope=Permission.SCOPE_PROJECT, code='project.export', description='Export')
        role = ProjectRole.objects.create(company=self.company_a, name='Exporter', description='Exporter')
        ProjectRolePermission.objects.create(role=role, permission=perm, effect='ALLOW')
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                ProjectRolePermission.objects.create(role=role, permission=perm, effect='ALLOW')

        bad_perm = Permission.objects.create(scope=Permission.SCOPE_PROJECT, code='project.export.bad', description='Export Bad')
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                ProjectRolePermission.objects.create(role=role, permission=bad_perm, effect='BAD')
