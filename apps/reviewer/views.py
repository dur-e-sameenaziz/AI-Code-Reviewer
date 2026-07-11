from django.shortcuts import render

from .forms import CodeReviewForm
from .services import CodeReviewerService, ReviewServiceError


def create_review(request):
    review = None
    markdown_review = ""
    error = ""

    if request.method == "POST":
        form = CodeReviewForm(request.POST)

        if form.is_valid():
            try:
                review = CodeReviewerService().review(
                    code=form.cleaned_data["code"],
                    language=form.cleaned_data["language"],
                )
                markdown_review = CodeReviewerService.markdown(review)
            except ReviewServiceError as exc:
                error = str(exc)
    else:
        form = CodeReviewForm()

    return render(
        request,
        "reviewer/review_form.html",
        {
            "form": form,
            "review": review,
            "markdown_review": markdown_review,
            "error": error,
        },
    )
