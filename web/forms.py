from django.forms import ModelForm, ValidationError
from websvcs.models import EmailSubscription

class EmailSubscriptionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailSubscriptionForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Email Address'
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if EmailSubscription.objects.filter(email=email).count() > 0:
            raise ValidationError('Email already in use. Please provide another one.')
        return email
    
    class Meta:
        model = EmailSubscription
        fields = ['email']


    