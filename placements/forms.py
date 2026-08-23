from django import forms
from django.contrib.auth.models import User
from .models import Student, Application


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['branch', 'cgpa', 'backlogs', 'skills', 'phone', 'resume']
        widgets = {
            'skills': forms.TextInput(attrs={'placeholder': 'Python, Django, HTML, CSS'}),
        }


class ApplicationUpdateForm(forms.ModelForm):
    """Used by a Company to update an applicant's status and interview details."""
    class Meta:
        model = Application
        fields = ['status', 'remarks', 'interview_datetime', 'interview_mode', 'interview_location']
        widgets = {
            'interview_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'interview_location': forms.TextInput(
                attrs={'placeholder': 'Room 204, or https://meet.google.com/...'}
            ),
        }
