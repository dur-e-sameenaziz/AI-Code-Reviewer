import json

from django.conf import settings
from openai import OpenAI


class ReviewServiceError(Exception):
    pass


PROMPT = """
You are a senior software engineer reviewing a short code snippet before human code review.

The snippet may be:
- a small independent function
- part of a larger application
- a framework-specific method, model, controller, service, serializer, job, or query
- incomplete because surrounding project context is not shown

Review it like an experienced engineer, not like a generic lint tool.

Important judgment rules:
- Do not assume missing surrounding context is a bug.
- Do not require null checks, validations, authorization checks, or error handling unless the snippet itself gives a real reason to expect them.
- Do not penalize idiomatic framework or language patterns.
- Do not over-comment on style, formatting, or naming unless it affects readability or maintainability.
- If something depends on project conventions or associations not shown, say that context may be needed instead of calling it wrong.
- Focus on issues a strong engineer in the specified language/framework would genuinely raise.
- Be especially careful with framework associations, ORM relations, chained queries, callbacks, serializers, scopes, decorators, and service objects.
- A short snippet can be valid if the surrounding application owns validations, permissions, null safety, or setup elsewhere.

Review for:
- readability
- structure
- maintainability
- obvious correctness risks
- unnecessary complexity
- performance concerns
- performance concerns that are visible from the snippet
- testability where the snippet itself suggests missing edge cases

Return only JSON with this shape:
{
  "summary": "one practical sentence about the overall code quality",
  "readability": {"score": 1, "feedback": "one short reason"},
  "structure": {"score": 1, "feedback": "one short reason"},
  "maintainability": {"score": 1, "feedback": "one short reason"},
  "risks": [
    {"severity": "low|medium|high", "risk": "one short sentence"}
  ],
  "improvements": [
    {"title": "short title", "reason": "why it matters", "suggestion": "one concrete suggestion"}
  ],
  "positive_note": "one specific thing the code does well",
  "overall_score": 1,
  "verdict": "max 4 words"
}

Rules:
- Recommend exactly three improvements only if there are three meaningful issues.
- If there are fewer than three real issues, return fewer improvements.
- Be fair and calibrated: most working code should score between 5 and 8.
- Reserve low scores for code that is broken, unsafe, or genuinely hard to maintain.
- Reserve 9-10 for unusually clean and well-structured code.
- Keep the tone constructive and human.
- Do not invent business requirements.
- Do not repeat the same point in multiple sections.
- Do not include markdown, code fences, or any text outside the JSON object.
""".strip()


class CodeReviewerService:
    def review(self, code, language):
        if not settings.OPENAI_API_KEY:
            raise ReviewServiceError("OPENAI_API_KEY is not configured.")

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        try:
            response = client.responses.create(
                model=settings.OPENAI_MODEL,
                input=[
                    {"role": "system", "content": PROMPT},
                    {
                        "role": "user",
                        "content": f"Language: {language}\n\nCode:\n{code}",
                    },
                ],
            )
            review = json.loads(response.output_text)
        except Exception as exc:
            raise ReviewServiceError("Could not create the review. Please try again.") from exc

        self.validate_review(review)

        return review

    def validate_review(self, review):
        required_fields = [
            "summary",
            "readability",
            "structure",
            "maintainability",
            "risks",
            "improvements",
            "positive_note",
            "overall_score",
            "verdict",
        ]
        missing_fields = [field for field in required_fields if field not in review]

        if missing_fields:
            raise ReviewServiceError("The AI response was missing required review fields.")

        if len(review.get("improvements", [])) > 3:
            raise ReviewServiceError("The AI response returned too many improvements.")

        if not isinstance(review.get("risks"), list):
            raise ReviewServiceError("The AI response returned invalid risks.")

        for risk in review.get("risks", []):
            if not isinstance(risk, dict):
                raise ReviewServiceError("The AI response returned invalid risks.")

            if risk.get("severity") not in {"low", "medium", "high"}:
                raise ReviewServiceError("The AI response returned an invalid risk severity.")

    @staticmethod
    def markdown(review):
        text = f"# Code Review\n\nScore: {review.get('overall_score', '-')}/10\n\n"
        text += f"Verdict: {review.get('verdict', '-')}\n\n"
        text += f"Summary: {review.get('summary', '')}\n\n"

        text += "Scores:\n"
        text += CodeReviewerService.score_line("Readability", review.get("readability", {}))
        text += CodeReviewerService.score_line("Structure", review.get("structure", {}))
        text += CodeReviewerService.score_line("Maintainability", review.get("maintainability", {}))

        text += "\nRisks:\n"
        risks = review.get("risks", [])
        if risks:
            for item in risks:
                text += f"- [{item.get('severity', '-').upper()}] {item.get('risk', '')}\n"
        else:
            text += "- No notable risks found.\n"

        text += "\nImprovements:\n"
        improvements = review.get("improvements", [])
        if improvements:
            for item in improvements:
                text += f"- {item.get('title', '')}: {item.get('suggestion', '')}\n"
        else:
            text += "- No high-value improvements needed.\n"

        text += "\nPositive note:\n"
        text += review.get("positive_note", "")
        return text

    @staticmethod
    def score_line(label, score):
        return f"- {label}: {score.get('score', '-')}/10 - {score.get('feedback', '')}\n"
