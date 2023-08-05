from . import models
from django import forms
from datetime import date, timedelta
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
import re


class CommentForm(forms.ModelForm):
    """
    A form for the comments, for authenticated users, found in report details.
    """
    class Meta:
        model = models.Comment
        fields = ('content',)


class CreateReportForm(forms.ModelForm):
    """
    The form for creating a report.
    Also used in the edit_report view with prepopulated fields.
    """
    class Meta:
        model = models.Report
        fields = [
            'title',
            'start_date',
            'end_date',
            'time_taken',
            'goal_reached',
            'height_in_meters',
            'overall_conditions',
            'activity_category',
            'description',
            'number_in_group',
            'number_on_route',
            'gps_map_link',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super(CreateReportForm, self).__init__(*args, **kwargs)

        self.fields['title'] = forms.CharField(
            label="Route Name", initial="e.g. Eiger, Heckmair")
        self.fields['goal_reached'].label = "Goal achieved?"
        self.fields['start_date'] = forms.DateField(
            widget=forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': str(date.today())
                    }),
        )
        self.fields['end_date'] = forms.DateField(
            widget=forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': str(date.today())
                    }),
        )
        self.fields['time_taken'].widget.attrs.update({
            'placeholder': 'hh:mm:ss', 'required': False,
        })
        self.fields['height_in_meters'].label = "Summit height (masl)"
        self.fields['status'].label = "Publish/ Draft"
        self.fields['gps_map_link'].required = False

    # Validators

    def clean_title(self):
        """
        Custom clean method to validate the title field.
        Title should be greater than 3 characters, less than 30 characters,
        and should not only contain numbers.
        """
        title = self.cleaned_data.get('title')

        if len(title) < 3 or len(title) > 30:
            raise forms.ValidationError(
                "Title must be between 3 and 30 characters.")

        if title.isdigit():
            raise forms.ValidationError("Title cannot be just numbers.")

        return title

    def clean_start_date(self):
        """
        Validate the start_date field.
        The start date should not be before five years prior to report creation.
        """
        start_date = self.cleaned_data.get('start_date')
        five_years_ago = date.today() - timedelta(days=365*5)

        if start_date < five_years_ago:
            raise forms.ValidationError(
                """Start date must not be more than
                 5 years old, it keeps our reports current!""")

        return start_date

    def clean_end_date(self):

        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError(
                "End date cannot be before start date.")
        return end_date

    def clean_time_taken(self):
        """
        Validates the time_taken field
        returns ValidationError to user if invalid input.
        """
        time_taken = self.data.get('time_taken')

        if time_taken is None or 'hh:mm:ss':
            return None

        if not re.match(r'^\d{2}:\d{2}:\d{2}$', time_taken):
            raise forms.ValidationError("Invalid time format. Use hh:mm:ss.")

        return time_taken


class ImageFileForm(forms.ModelForm):
    """
    The form to handle image file uploads within the create report template.
    """
    class Meta:
        model = models.ImageFile
        fields = ['image_file']


class UpdateAccountForm(UserChangeForm):
    """
    Form used for updated account information; username and email.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.pop('password')
        self.fields['username'].label = "Update Username"
        self.fields['email'].label = "Update Email"
