from unittest.mock import patch
from django.test import TestCase
from celery.exceptions import MaxRetriesExceededError

from analysis.models import Analysis
from analysis.tasks import run_ai_analysis
from documents.models import CV, JobOffer
from users.models import CustomUser


class AnalysisTaskTests(TestCase):
    def setUp(self):
        self.candidate = CustomUser.objects.create_user(
            username="john",
            password="PAAAassword!2@",
            email="example@example.com",
            phone_number="1234567879",
            role=CustomUser.Role.CANDIDATE
        )

        self.recruiter = CustomUser.objects.create_user(
            username="kate",
            password="PAAAassword!2@",
            email="recruiter@example.com",
            phone_number="1234567878",
            role=CustomUser.Role.RECRUITER
        )

        self.cv = CV.objects.create(owner=self.candidate, raw_text="Python Django developer CV", status=CV.Status.PROCESSED)
        self.job_offer = JobOffer.objects.create(
            owner=self.recruiter,
            title="Python Dev",
            skills="Python, Django, AWS",
            raw_text="Looking for a Python Django developer."
        )

        self.analysis = Analysis.objects.create(cv=self.cv, job_offer=self.job_offer)

    @patch('analysis.services.gemini_client.get_ai_analysis', return_value=(88.5, ["AWS"]))
    def test_run_ai_analysis_success_path(self, mock_ai):
        # Task should fetch analysis, invoke AI service, update score, missing skills and set status=DONE
        run_ai_analysis(self.analysis.id)

        self.analysis.refresh_from_db()
        self.assertEqual(float(self.analysis.match_score), 88.5)
        self.assertEqual(self.analysis.missing_skills, ["AWS"])
        self.assertEqual(self.analysis.status, Analysis.Status.DONE)
        mock_ai.assert_called_once()

    @patch('analysis.services.gemini_client.get_ai_analysis', return_value=(90.0, []))
    def test_run_ai_analysis_idempotency_when_already_processing_or_done(self, mock_ai):
        # Task should abort early without invoking AI service if already processing or done
        self.analysis.status = Analysis.Status.PROCESSING
        self.analysis.save()

        run_ai_analysis(self.analysis.id)

        mock_ai.assert_not_called()

        self.analysis.status = Analysis.Status.DONE
        self.analysis.save()

        run_ai_analysis(self.analysis.id)
        mock_ai.assert_not_called()

    @patch('analysis.services.gemini_client.get_ai_analysis', side_effect=Exception("API Error"))
    def test_run_ai_analysis_failure_path_sets_status_failed(self, mock_ai):
        # When AI call raises exception and max retries are exceeded, status should transition to FAILED
        with patch.object(run_ai_analysis, 'retry', side_effect=MaxRetriesExceededError()):
            run_ai_analysis(self.analysis.id)

        self.analysis.refresh_from_db()
        self.assertEqual(self.analysis.status, Analysis.Status.FAILED)
