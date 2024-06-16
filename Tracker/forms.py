from django import forms
from django.contrib.auth.hashers import make_password
from captcha.fields import CaptchaField
from django.contrib.auth.forms import PasswordChangeForm
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
    company_email = forms.EmailField(required=False)
    captcha = CaptchaField()

    def _init_(self, *args, **kwargs):
        super(SignUpForm, self)._init_(*args, **kwargs)
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

            company = self.cleaned_data.get('company')
            if not company:
                company_name = self.cleaned_data.get('company_name')
                if company_name:
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
    name = forms.CharField(max_length=30)
    url = forms.URLField(widget=forms.Textarea)

    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'})
        }

    def _init_(self, *args, **kwargs):
        super(ProductForm, self)._init_(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['company'].queryset = Company.objects.all()


class IssueForm(forms.ModelForm):
    company_name = forms.CharField(max_length=100, required=False)
    company_url = forms.URLField(required=False)
    company_bio = forms.CharField(widget=forms.Textarea, required=False)
    company_pic = forms.ImageField(required=False)
    company_email = forms.EmailField(required=False)
    product_name = forms.CharField(max_length=100, required=False)
    product_url = forms.URLField(required=False)

    class Meta:
        model = Issue
        fields = ['issuename', 'description', 'company', 'product', 'tags']

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['product'].required = False
        self.fields['company'].queryset = Company.objects.all()
        self.fields['product'].queryset = Product.objects.none()
        

        if 'company' in self.data and self.data.get('company') != '':
            try:
                company_id = self.data.get('company')
                self.fields['product'].queryset = Product.objects.filter(company_id=company_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            try:
                if self.instance.company:
                    self.fields['product'].queryset = self.instance.company.product_set.all()
            except Company.DoesNotExist:
                self.fields['product'].queryset = Product.objects.none()


    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get('company')
        product_list = self.data.getlist('product')
        product = None


        if product_list and product_list[0] != '':
            try:
                product_id = product_list[0]
                product = Product.objects.get(id=product_id)
                cleaned_data['product'] = product
            except (Product.DoesNotExist, IndexError):
                self.add_error('product', "Selected product does not exist.")


        if not company:
            for field in ['company_name', 'company_url', 'company_email', 'company_bio', 'company_pic']:
                if not cleaned_data.get(field):
                    self.add_error(field, f"{field.replace('_', ' ').capitalize()} is required if no company is selected.")

        if company and not product:
            for field in ['product_name', 'product_url']:
                if not cleaned_data.get(field):
                    self.add_error(field, f"{field.replace('_', ' ').capitalize()} is required if no product is selected.")

        return cleaned_data

    def save(self, commit=True):
        issue = super().save(commit=False)
        company = self.cleaned_data.get('company')
        product = self.cleaned_data.get('product')

        if company:
            issue.company = company
        else:
            company_name = self.cleaned_data.get('company_name')
            if company_name:
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
                issue.company = company

        if product:
            issue.product = product
        else:
            product_name = self.cleaned_data.get('product_name')
            if product_name:
                product_url = self.cleaned_data.get('product_url')
                product = Product.objects.create(
                    name=product_name,
                    url=product_url,
                    company=company 
                )
                issue.product = product

        if commit:
            issue.save()

        return issue
class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'username', 'image']


class EditIssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['issuename', 'description', 'tags']


class IssueStatusForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }


class IssueFilterForm(forms.Form):
    status = forms.ChoiceField(choices=Issue.STATUS_CHOICES, required=False)
    created_by = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False)
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False)
    tags = forms.CharField(max_length=255, required=False)


class SupportQueryForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['type', 'message']

class HiringRequestForm(forms.ModelForm):
    class Meta:
        model = Hiring
        fields = ['name', 'url', 'options', 'description']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['options', 'bool', 'comment']
class EditFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['options', 'bool', 'comment']