from rest_framework import permissions

class IsCVOwnerOrRecruiter(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True
        
        cvs = obj.analysis_cvs.all()
        if cvs.filter(job_offer__owner = request.user).exists():
            return True

        return False
        
class IsJobOfferOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True

        return False
