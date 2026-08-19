from django.db import models
from users.models import CustomUser

class CV(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name = "cvs"
        )

    file = models.FileField(
        upload_to='cv_files/',
        )
    raw_text = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSED = "processed", "Processed"
        FAILED = "failed","Failed"

    status = models.CharField(choices=Status.choices,
                            default="pending",
                            max_length=9)

class JobOffer(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name = "job_offers"
        )
    title = models.CharField(max_length=30)
    raw_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)