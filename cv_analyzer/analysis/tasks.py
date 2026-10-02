from celery import shared_task
from django.db import transaction

@shared_task(bind=True, ignore_result=True, max_retries=3)
def run_ai_analysis(self, analysis_id):
    """
    Fetch Analysis by ID, run AI scoring, and save results.
    Guarantees idempotency via select_for_update and status checking.
    """
    # Imports inside a task - Django must already be loaded when the task executes
    from analysis.models import Analysis
    from documents.utils import get_ai_analysis

    try:
        with transaction.atomic():
            analysis = Analysis.objects.select_for_update().get(id=analysis_id)

            if analysis.status in (Analysis.Status.PROCESSING, Analysis.Status.DONE):
                return

            analysis.status = Analysis.Status.PROCESSING
            analysis.save(update_fields=['status'])

        score, missing = get_ai_analysis(
            analysis.cv.raw_text,
            analysis.job_offer
        )

        analysis.match_score = score
        analysis.missing_skills = missing
        analysis.status = Analysis.Status.DONE
        analysis.save()

    except Exception as err:
        try:
            raise self.retry(exc=err, countdown=30)
        except self.MaxRetriesExceededError:
            # filter().first() returns None instead of raising DoesNotExist
            analysis = Analysis.objects.filter(id=analysis_id).first()
            if analysis:
                analysis.status = Analysis.Status.FAILED
                analysis.save()