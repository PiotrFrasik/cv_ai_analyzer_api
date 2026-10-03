from rest_framework import permissions

class IsCVOwnerOrRecruiter(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True
        
        analyses = obj.analyses.all()
        if analyses.filter(job_offer__owner=request.user).exists():
            return True

        return False
        
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner