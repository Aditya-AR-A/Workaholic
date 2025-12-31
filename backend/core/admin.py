from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Company, Profile, Department, Designation, Employee,
    Attendance, TimeLog, Break, Overtime, EmployeeRoutineTimings, RoutineTemplate,
    LeaveType, LeaveRequest, Notification, Client, Project, ProjectUser,
    TicketType, Ticket, TicketAssignee, TicketUpdate, TicketAttachement, TicketComment
)

admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Profile)
admin.site.register(Department)
admin.site.register(Designation)
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(TimeLog)
admin.site.register(Break)
admin.site.register(Overtime)
admin.site.register(EmployeeRoutineTimings)
admin.site.register(RoutineTemplate)
admin.site.register(LeaveType)
admin.site.register(LeaveRequest)
admin.site.register(Notification)
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(ProjectUser)
admin.site.register(TicketType)
admin.site.register(Ticket)
admin.site.register(TicketAssignee)
admin.site.register(TicketUpdate)
admin.site.register(TicketAttachement)
admin.site.register(TicketComment)
