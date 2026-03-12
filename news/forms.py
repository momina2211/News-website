import re
from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Submit, HTML

from .models import Article

TAILWIND_INPUT_CLASS = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"


class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT_CLASS,
            'placeholder': 'Search articles...',
            'hx-get': '/search/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#search-results',
        })
    )


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'content', 'excerpt', 'category',
            'image', 'published_date', 'status', 'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': TAILWIND_INPUT_CLASS,
                'id': 'id_title',
            }),
            'slug': forms.TextInput(attrs={
                'class': TAILWIND_INPUT_CLASS,
                'id': 'id_slug',
            }),
            'content': forms.Textarea(attrs={
                'class': TAILWIND_INPUT_CLASS,
                'rows': 10,
            }),
            'excerpt': forms.Textarea(attrs={
                'class': TAILWIND_INPUT_CLASS,
                'rows': 3,
            }),
            'category': forms.Select(attrs={
                'class': TAILWIND_INPUT_CLASS,
            }),
            'published_date': forms.DateTimeInput(attrs={
                'class': TAILWIND_INPUT_CLASS,
                'type': 'datetime-local',
            }),
            'status': forms.Select(attrs={
                'class': TAILWIND_INPUT_CLASS,
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column(Field('title'), css_class='w-full md:w-1/2 px-2'),
                Column(Field('slug'), css_class='w-full md:w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2 mb-4',
            ),
            Row(
                Column(Field('category'), css_class='w-full md:w-1/3 px-2'),
                Column(Field('status'), css_class='w-full md:w-1/3 px-2'),
                Column(Field('is_featured'), css_class='w-full md:w-1/3 px-2'),
                css_class='flex flex-wrap -mx-2 mb-4',
            ),
            Row(
                Column(Field('excerpt'), css_class='w-full px-2'),
                css_class='flex flex-wrap -mx-2 mb-4',
            ),
            Row(
                Column(Field('content'), css_class='w-full px-2'),
                css_class='flex flex-wrap -mx-2 mb-4',
            ),
            Row(
                Column(Field('image'), css_class='w-full md:w-1/2 px-2'),
                Column(Field('published_date'), css_class='w-full md:w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2 mb-4',
            ),
            Submit(
                'submit',
                'Save Article',
                css_class='bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg',
            ),
        )

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '')
        if not re.match(r'^[a-z0-9-]+$', slug):
            raise forms.ValidationError(
                'Invalid slug: only lowercase letters (a-z), digits (0-9), and hyphens (-) are allowed. '
                'No spaces or special characters.'
            )
        return slug

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        published_date = cleaned_data.get('published_date')
        if status == 'published' and not published_date:
            cleaned_data['published_date'] = timezone.now()
        return cleaned_data


class ArticleDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        label='I confirm I want to delete this article',
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('confirm'),
            Submit(
                'submit',
                'Delete Article',
                css_class='bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-lg',
            ),
        )
