from django import forms
from .models import Project, CreditListing
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'project_type', 'location']

class ListingForm(forms.ModelForm):
    class Meta:
        model = CreditListing
        fields = ['available_credits', 'price_per_credit', 'available']

class BuyerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
