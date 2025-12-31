from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True)
    manager_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_users')
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_timer = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

class Company(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    domain = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_companies')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_companies')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    personal_email = models.EmailField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True, verbose_name="emergency contact name")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name="emergency contact phone")
    alternate_email = models.EmailField(blank=True, verbose_name="alternate email")
    alternate_phone = models.CharField(max_length=20, blank=True, verbose_name="alternate phone")
    dob = models.DateField(null=True, blank=True, verbose_name="date of birth")
    gender = models.CharField(max_length=10, blank=True, verbose_name="gender")
    blood_group = models.CharField(max_length=10, blank=True, verbose_name="blood group")
    additional_info = models.TextField(blank=True, verbose_name="additional information")
    medical_history = models.TextField(blank=True, verbose_name="medical history")
    marital_status = models.CharField(max_length=10, blank=True, verbose_name="marital status")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_profiles')

    def __str__(self):
        return f"Profile of {self.user.email}"

class Department(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Designation(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

class Attendance(models.Model):
    """
    Daily Attendance Snapshot.
    Summarizes the day's activity (Total hours, overall status).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_attendances')
    date = models.DateField()
    
    # Summary fields (calculated from TimeLogs)
    total_worked_seconds = models.IntegerField(default=0)
    overtime_seconds = models.IntegerField(default=0)
    
    is_late = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='PENDING')  # PRESENT, ABSENT, HALF_DAY, LEAVE
    
    # Legacy fields kept for migration compatibility (optional usage)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    check_out_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by_manager = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'date']

    def update_summary(self):
        """Recalculate totals based on TimeLogs."""
        logs = self.timelogs.filter(check_out__isnull=False)
        total_seconds = 0
        for log in logs:
            duration = (log.check_out - log.check_in).total_seconds()
            total_seconds += duration
        
        self.total_worked_seconds = int(total_seconds)
        
        # Simple Overtime Logic (Standard 8 hours = 28800 seconds)
        STANDARD_WORK_SECONDS = 8 * 3600
        if self.total_worked_seconds > STANDARD_WORK_SECONDS:
            self.overtime_seconds = self.total_worked_seconds - STANDARD_WORK_SECONDS
            self.status = 'OVERTIME'
        elif self.total_worked_seconds > 0:
            self.status = 'PRESENT'
        
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.date}"

class TimeLog(models.Model):
    """
    Master Attendance Record (Audit Trail).
    Stores specific check-in/check-out events.
    """
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='timelogs')
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    
    check_in_reason = models.TextField(blank=True, help_text="Reason for this check-in")
    check_out_reason = models.TextField(blank=True, help_text="Reason for checking out")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.check_out and self.check_in and self.check_out <= self.check_in:
            raise ValidationError("Check-out time must be after check-in time.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.attendance.update_summary()

class Break(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    break_in = models.TimeField(null=True, blank=True)
    break_out = models.TimeField(null=True, blank=True)
    approved_break_duration_seconds = models.IntegerField(default=0)

class Overtime(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    overtime_seconds = models.IntegerField(default=0)
    overtime = models.BooleanField(default=False)

class EmployeeRoutineTimings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    late_grace_period_seconds = models.IntegerField(default=0)
    early_leave_grace_period_seconds = models.IntegerField(default=0)
    minimum_work_hours_seconds = models.IntegerField(default=0)
    maximum_work_hours_seconds = models.IntegerField(default=0)
    approved_break_duration_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class RoutineTemplate(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    late_grace_period_seconds = models.IntegerField(default=0)
    early_leave_grace_period_seconds = models.IntegerField(default=0)
    minimum_work_hours_seconds = models.IntegerField(default=0)
    maximum_work_hours_seconds = models.IntegerField(default=0)
    approved_break_duration_seconds = models.IntegerField(default=0)
    for_designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class LeaveRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=4000)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='approved_leaves')

# --- Notification System ---

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=[
        ('ATTENDANCE_ALERT', 'Attendance Alert'),
        ('LEAVE_UPDATE', 'Leave Update'),
        ('TICKET_UPDATE', 'Ticket Update'),
        ('GENERAL', 'General')
    ])
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    attached_to_company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    attached_to_company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['project', 'user']

class TicketType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    priority = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class TicketAssignee(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ['ticket', 'user']

class TicketUpdate(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    update = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10)
    priority = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

class TicketAttachement(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    for_ticket_update = models.ForeignKey(TicketUpdate, on_delete=models.CASCADE)
    attachement = models.FileField(upload_to="ticket_attachements/")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    for_ticket_update = models.ForeignKey(TicketUpdate, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    attached_to_company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
