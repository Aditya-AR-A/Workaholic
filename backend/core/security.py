from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)

class IsCompanyAdmin(permissions.BasePermission):
    """
    Allows access to Company Admins.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin and request.user.company)

class IsSameCompany(permissions.BasePermission):
    """
    Object-level permission to only allow access to objects within the same company.
    Assumes the model instance has a `company` attribute or related `user.company`.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
            
        if not request.user.company:
            return False

        # If object is User, check their company
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
        
        # If object has a user fk, check that user's company
        if hasattr(obj, 'user') and hasattr(obj.user, 'company'):
            return obj.user.company == request.user.company
            
        # If object has attached_to_company
        if hasattr(obj, 'attached_to_company'):
            return obj.attached_to_company == request.user.company

        return False