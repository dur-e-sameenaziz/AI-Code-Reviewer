from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from .forms import CodeReviewForm
from .services import CodeReviewerService, ReviewServiceError


def sample_review():
    return {
        "summary": "Good start.",
        "readability": {"score": 7, "feedback": "Easy to read."},
        "structure": {"score": 6, "feedback": "Could be split up."},
        "maintainability": {"score": 6, "feedback": "Needs tests."},
        "risks": [{"severity": "medium", "risk": "No error handling."}],
        "improvements": [
            {"title": "Add tests", "reason": "Safer changes.", "suggestion": "Write a few unit tests."},
            {"title": "Handle errors", "reason": "Avoid crashes.", "suggestion": "Add try/except where useful."},
        ],
        "positive_note": "The main idea is simple.",
        "overall_score": 7,
        "verdict": "Needs minor changes",
    }


class CodeReviewFormTests(SimpleTestCase):
    def test_valid_form(self):
        form = CodeReviewForm(
            data={
                "language": "python",
                "code": "def add(a, b):\n    return a + b",
            }
        )
        self.assertTrue(form.is_valid())

    def test_short_code_is_invalid(self):
        form = CodeReviewForm(
            data={"language": "python", "code": "x=1"}
        )
        self.assertFalse(form.is_valid())


class FakeResponses:
    def __init__(self, text):
        self.text = text

    def create(self, **kwargs):
        return SimpleNamespace(output_text=self.text)


class FakeClient:
    def __init__(self, text):
        self.responses = FakeResponses(text)


class CodeReviewerServiceTests(SimpleTestCase):
    @override_settings(OPENAI_API_KEY="", OPENAI_MODEL="test-model")
    def test_missing_key_raises_error(self):
        with self.assertRaises(ReviewServiceError):
            CodeReviewerService().review("def x(): pass", "python")

    @override_settings(OPENAI_API_KEY="fake", OPENAI_MODEL="test-model")
    def test_review_returns_json(self):
        with patch("apps.reviewer.services.OpenAI", return_value=FakeClient(__import__("json").dumps(sample_review()))):
            result = CodeReviewerService().review("def x(): pass", "python")

        self.assertEqual(result["overall_score"], 7)
        self.assertEqual(len(result["improvements"]), 2)

    @override_settings(OPENAI_API_KEY="fake", OPENAI_MODEL="test-model")
    def test_review_rejects_more_than_three_improvements(self):
        review = sample_review()
        review["improvements"].append(
            {"title": "Rename variables", "reason": "Clearer code.", "suggestion": "Use names that explain intent."}
        )
        review["improvements"].append(
            {"title": "Split method", "reason": "Too much work.", "suggestion": "Extract a helper."}
        )

        with patch("apps.reviewer.services.OpenAI", return_value=FakeClient(__import__("json").dumps(review))):
            with self.assertRaises(ReviewServiceError):
                CodeReviewerService().review("def x(): pass", "python")


class ReviewViewTests(SimpleTestCase):
    def test_form_page_loads(self):
        response = self.client.get(reverse("reviewer:create_review"))
        self.assertEqual(response.status_code, 200)

    @override_settings(OPENAI_API_KEY="fake", OPENAI_MODEL="test-model")
    def test_review_result_renders_on_form_page(self):
        with patch("apps.reviewer.services.OpenAI", return_value=FakeClient(__import__("json").dumps(sample_review()))):
            response = self.client.post(
                reverse("reviewer:create_review"),
                data={
                    "language": "python",
                    "code": "def add(a, b):\n    return a + b",
                },
            )

        self.assertContains(response, "Needs minor changes")
