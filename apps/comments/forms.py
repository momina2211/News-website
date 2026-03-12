"""Comments forms"""
from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 "
                         "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 "
                         "focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none",
                "rows": 4,
                "placeholder": "Share your thoughts...",
                "maxlength": 1000,
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if len(content) < 5:
            raise forms.ValidationError("Comment is too short (minimum 5 characters).")
        if len(content) > 1000:
            raise forms.ValidationError("Comment is too long (maximum 1000 characters).")
        # Basic spam check: repeated characters
        if any(char * 10 in content for char in "abcdefghijklmnopqrstuvwxyz!?. "):
            raise forms.ValidationError("Your comment appears to be spam.")
        return content

