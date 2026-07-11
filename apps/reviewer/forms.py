from django import forms


class CodeReviewForm(forms.Form):
    LANGUAGE_CHOICES = [
        ("python", "Python"),
        ("ruby", "Ruby"),
        ("javascript", "JavaScript"),
        ("typescript", "TypeScript"),
        ("other", "Other"),
    ]

    language = forms.ChoiceField(choices=LANGUAGE_CHOICES)
    code = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 15,
                "placeholder": "Paste a short code snippet here",
            }
        )
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip()

        if len(code) < 10:
            raise forms.ValidationError("Please paste a bigger code snippet.")

        if len(code) > 12000:
            raise forms.ValidationError("Please keep the code under 12,000 characters.")

        return code
