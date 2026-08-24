from rest_framework import permissions

class IsRecruiterOrCVOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Recruiter
        if request.user == obj.job_offer.owner:
            return True

        # Candidate
        if request.user == obj.cv.owner:
            return True

        return False