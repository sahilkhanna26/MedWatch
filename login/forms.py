from django import forms
from .models import Report

class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        exclude = ['reporter', 'published_date', 'status', 'resolved_notes']  #fields that do not show up when user is submitting a form, we do not want users to be able to set these values themselves

class ResolvedFeedbackForm(forms.Form):
    resolved_notes = forms.CharField(label='Resolution Details', widget=forms.Textarea, required=False)  #new form for site admin to submit text feedback
