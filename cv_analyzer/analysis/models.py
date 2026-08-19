from django.db import models
from documents.models import CV, JobOffer

class Analysis(models.Model):
    cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name = "analysis_cvs"
    )
    job_offer = models.ForeignKey(
        JobOffer,
        on_delete=models.CASCADE,
        related_name = "analysis_job_offers"
    )

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done","Done"
        FAILED = "failed","Failed"


    status = models.CharField(
        choices=Status.choices,
        default="pending",
        max_length=10
    )

    match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
    )
    