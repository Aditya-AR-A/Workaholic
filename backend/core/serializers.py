from rest_framework import serializers
from .models import (
    User, Company, Profile, Department, Designation, Employee,
    Attendance, TimeLog, LeaveRequest, LeaveType,
    Project, Client, Ticket, TicketType, TicketUpdate, TicketComment, TicketAttachement,
    Notification
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'company', 'is_employee', 'is_admin']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)
    designation = DesignationSerializer(read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'

class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    timelogs = TimeLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LeaveType.objects.all(), source='leave_type', write_only=True
    )
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), source='client', write_only=True
    )
    
    class Meta:
        model = Project
        fields = '__all__'

class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source='project', write_only=True
    )
    assigned_to = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'

class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketUpdate
        fields = '__all__'

class TicketAttachementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachement
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
