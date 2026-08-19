from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(
        unique=True,
        null=False,
        max_length=12 #ex. 123 456 789
    )

    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        RECRUITER = "recruiter", "Recruiter"

    role = models.CharField(
        blank=False, 
        choices=Role.choices, 
        max_length=10
    )

class CandidateProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )

    salary_min = models.IntegerField()
    salary_max = models.IntegerField()

    city = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    
class RecruiterProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recruiter_profile'
    )
    department = models.CharField(max_length=30)