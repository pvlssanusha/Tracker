from django import forms
from django.contrib.auth.hashers import make_password
# from tagify import TagifyWidget

from django import forms
from .models import *

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'firstname', 'lastname', 'email', 'company']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'})
        }

    company_name = forms.CharField(max_length=100, required=False)
    company_url = forms.URLField(required=False)
    company_bio = forms.CharField(widget=forms.Textarea, required=False)
    company_pic = forms.ImageField(required=False)
    company_email=forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['company'].queryset = Company.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            raise forms.ValidationError("Password and confirm password do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()

            # Check if company is selected or new company info is provided
            company = self.cleaned_data.get('company')
            if not company:
                company_name = self.cleaned_data.get('company_name')
                if company_name:
                    # If company name is provided, create a new company
                    company_url = self.cleaned_data.get('company_url')
                    company_bio = self.cleaned_data.get('company_bio')
                    company_pic = self.cleaned_data.get('company_pic')
                    company_email = self.cleaned_data.get('company_email')

                    company = Company.objects.create(
                        name=company_name,
                        url=company_url,
                        bio=company_bio,
                        pic=company_pic,
                        email=company_email
                    )
                    user.company = company
                    user.save()

        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields="__all__"
    name=forms.CharField(max_length=30)
    url=forms.URLField(widget=forms.Textarea)
    widgets = {
            'company': forms.Select(attrs={'class': 'form-control'})
        }
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['company'].queryset = Company.objects.all()


from django import forms
from .models import Issue
import json

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['issuename', 'description', 'created_by', 'company', 'product', 'tags']
        # widgets = {
        #    'tags': TagifyWidget(),
        # }

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['tags'].required = False

    # def clean_tags(self):
    #     tags = self.cleaned_data['tags']
    #     try:
    #         tag_list = json.loads(tags)
    #         if not isinstance(tag_list, list):
    #             raise forms.ValidationError("Invalid format for tags.")
    #         return tag_list
    #     except json.JSONDecodeError:
    #         raise forms.ValidationError("Invalid format for tags.")



