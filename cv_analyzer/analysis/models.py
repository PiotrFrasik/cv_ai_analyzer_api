from django.db import models
from documents.models import CV, JobOffer

class Analysis(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name="analyses"
    )

    job_offer = models.ForeignKey(
        JobOffer,
        on_delete=models.CASCADE,
        related_name="analyses"
    )

    status = models.CharField(
        choices=Status.choices,
        default=Status.PENDING,
        max_length=10
    )

    match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
    )

    missing_skills = models.JSONField(
        default=list,
        blank=True
    )

    class Meta:
        verbose_name_plural = "analysis"
        constraints = [
            models.UniqueConstraint(fields=['cv', 'job_offer'], name='unique_cv_job_offer')
        ]
