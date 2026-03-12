"""Articles forms"""
from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = (
            "title", "summary", "content", "featured_image",
            "featured_image_caption", "category", "tags",
            "meta_description",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "Article title..."}),
            "summary": forms.Textarea(attrs={"class": "form-textarea", "rows": 3, "placeholder": "Brief summary..."}),
            "content": forms.Textarea(attrs={"class": "form-textarea", "rows": 20, "id": "article-content"}),
            "featured_image_caption": forms.TextInput(attrs={"class": "form-input"}),
            "meta_description": forms.TextInput(attrs={"class": "form-input", "placeholder": "SEO description (max 160 chars)"}),
            "tags": forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        if len(title) < 10:
            raise forms.ValidationError("Title must be at least 10 characters.")
        return title

    def clean_summary(self):
        summary = self.cleaned_data.get("summary", "")
        if len(summary) < 20:
            raise forms.ValidationError("Summary must be at least 20 characters.")
        return summary


class ArticleSearchForm(forms.Form):
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Search articles...",
            "autocomplete": "off",
        })
    )
    category = forms.CharField(max_length=100, required=False)

