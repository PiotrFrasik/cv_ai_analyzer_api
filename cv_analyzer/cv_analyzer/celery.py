import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cv_analyzer.settings')

app = Celery('cv_analyzer')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def run_ai_analysis(self, analysis_id):
    """
    Fetch Analysis by ID, run AI scoring, and save results.
    """
    # Imports inside a task - Django must already be loaded when the task executes
    from analysis.models import Analysis
    from documents.utils import get_ai_analysis

    try:
        analysis = Analysis.objects.get(id=analysis_id)

        score, missing = get_ai_analysis(
            analysis.cv.raw_text,
            analysis.job_offer
        )

        analysis.match_score = score
        analysis.missing_skills = missing
        analysis.status = Analysis.Status.DONE

        analysis.save()

    except Exception as err:
        # filter().first() returns None instead of raising DoesNotExist
        analysis = Analysis.objects.filter(id=analysis_id).first()
        if analysis:
            analysis.status = Analysis.Status.FAILED
            analysis.save()