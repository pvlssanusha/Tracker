from django import forms
from django.contrib.auth.hashers import make_password
from captcha.fields import CaptchaField
from django.contrib.auth.forms import PasswordChangeForm
from .models import *
from django.utils.safestring import mark_safe


class IssueStatusForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }
        help_texts = {
            'status': "Select the current status of the issue."
        }

    def __init__(self, *args, **kwargs):
        super(IssueStatusForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')
        status_choices = self.fields['status'].choices
        filtered_choices = [choice for choice in status_choices if choice[0] != 'created']
        self.fields['status'].choices = filtered_choices
      


class SignUpForm(forms.ModelForm):
    

    class Meta:
        model = User
        fields = ['username', 'firstname', 'lastname', 'email', 'company']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'})
        }
        help_texts = {
            'username': "Enter your desired username.",
            'firstname': "Enter your first name.",
            'lastname': "Enter your last name.",
            'email': "Enter your email address.",
            'company': "Select your company from the dropdown list or Create New Company by entering the below fields"
        }
    company_name = forms.CharField(max_length=100, required=False, help_text="Enter your company's name.")
    company_url = forms.URLField(required=False, help_text="Enter your company's website URL.")
    company_bio = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter a short biography for your company.")
    company_pic = forms.ImageField(required=False, help_text="Upload a picture for your company.")
    company_email = forms.EmailField(label="Company Email",required=False, help_text="Enter your company's contact email.")
    password = forms.CharField(label="Password",widget=forms.PasswordInput, help_text="Enter a strong password.")
    confirm_password = forms.CharField(label="Confirm Password",widget=forms.PasswordInput, help_text="Re-enter your password to confirm.")
    
    captcha = CaptchaField(label="Captcha",help_text="Enter the text from the image above.")

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['company'].queryset = Company.objects.all()
        self.fields['company'].widget.attrs.update({'class': 'company'})

        self.fields['company_name'].widget.attrs.update({'class': 'company-data'})
        self.fields['company_url'].widget.attrs.update({'class': 'company-data'})
        self.fields['company_bio'].widget.attrs.update({'class': 'company-data'})
        self.fields['company_pic'].widget.attrs.update({'class': 'company-data'})
        self.fields['company_email'].widget.attrs.update({'class': 'company-data'})
        self.fields['username'].label="User Name"
        self.fields['firstname'].label="First  Name"
        self.fields['lastname'].label="Last  Name"
        self.fields['company_name'].label="Company Name"
        self.fields['company_url'].label="Company URL"
        self.fields['company_bio'].label="Company Bio"
        self.fields['company_pic'].label="Company Pic"

        
        for field_name, field in self.fields.items():
            if field=="username":
                field.label="User Name"

            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

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
    name = forms.CharField(max_length=30, help_text="Enter the product name.")
    url = forms.URLField(widget=forms.Textarea, help_text="Enter the product URL.")

    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'})
        }
        help_texts = {
            'company': "Select the company associated with this product."
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['company'].queryset = Company.objects.all()
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')


class IssueForm(forms.ModelForm):
    company_name = forms.CharField(label="Company Name",max_length=100, required=False, help_text="Enter the company's name if not selecting from the list.")
    company_url = forms.URLField(label="Company URL",required=False, help_text="Enter the company's website URL if not selecting from the list.")
    company_bio = forms.CharField(label="Company Bio",widget=forms.Textarea, required=False, help_text="Enter a short biography for the company if not selecting from the list.")
    company_pic = forms.ImageField(label="Company Pic",required=False, help_text="Upload a picture for the company if not selecting from the list.")
    company_email = forms.EmailField(label="Company Email",required=False, help_text="Enter the company's contact email if not selecting from the list.")
    product_name = forms.CharField(label="Product Name",max_length=100, required=False, help_text="Enter the product's name if not selecting from the list.")
    product_url = forms.URLField(label="Product URL",required=False, help_text="Enter the product's URL if not selecting from the list.")
    tags_field = forms.CharField(label='Tags', required=False, widget=forms.TextInput(attrs={'class': 'tag-input'}))

    class Meta:
        model = Issue
        fields = ['issuename', 'description', 'company', 'product', 'tags_field','private']
        help_texts = {
            'issuename': "Enter the name of the issue.",
            'description': "Provide a detailed description of the issue.",
            'company': "Select the company associated with this issue.",
            'product': "Select the product associated with this issue.",
            'tags': "Enter tags related to the issue."
        }

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['product'].required = False
        self.fields['company'].queryset = Company.objects.all()
        self.fields['product'].queryset = Product.objects.none()
        
        self.fields['company'].widget.attrs.update({'class': 'company'})
        self.fields['product_url'].widget.attrs.update({'class': 'product-data'})
        self.fields['company_name'].widget.attrs.update({'class': 'company-data'})
        self.fields['company_url'].widget.attrs.update({'class': 'company-data'})
        self.fields['company_bio'].widget.attrs.update({'class': 'company-data'})
        self.fields['company_pic'].widget.attrs.update({'class': 'company-data'})
        self.fields['company_email'].widget.attrs.update({'class': 'company-data'})
        self.fields['product'].widget.attrs.update({'class': 'product'})
        self.fields['product_name'].widget.attrs.update({'class': 'product-data'})

        
        for field_name, field in self.fields.items():
            if field.required:
                
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

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
        tag_names = self.cleaned_data.get('tags', '')
        if tag_names:
            tag_list = tag_names.split(',')
            tags = []
            for tag_name in tag_list:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                tags.append(tag)
            issue.tags.set(tags)
        if commit:
            issue.save()

        return issue

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
        help_texts = {
            'old_password': "Enter your current password.",
            'new_password1': "Enter a new password.",
            'new_password2': "Re-enter the new password to confirm."
        }
class ReportIssueForm(forms.ModelForm):
    class Meta:
        model=ReportIssue
        fields = ['options','description']
    def __init__(self, *args, **kwargs):
        super(ReportIssueForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')
class ReportFeedbackForm(forms.ModelForm):
    class Meta:
        model=ReportFeedback
        fields = ['options','description']
    def __init__(self, *args, **kwargs):
        super(ReportFeedbackForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')
class ReportCommentForm(forms.ModelForm):
    class Meta:
        model=ReportComment
        fields = ['options','description']
    def __init__(self, *args, **kwargs):
        super(ReportCommentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

class ReportHiringCommentForm(forms.ModelForm):
    class Meta:
        model=ReportHiringComment
        fields = ['options','description']
    def __init__(self, *args, **kwargs):
        super(ReportHiringCommentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')





class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['image']
        help_texts = {
            'firstname': "Enter your first name.",
            'lastname': "Enter your last name.",
            'email': "Enter your email address.",
            'username': "Enter your desired username.",
            'image': "Upload a profile picture."
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')


class EditIssueForm(forms.ModelForm):
    tags_field = forms.CharField(label='Tags', required=False, widget=forms.TextInput(attrs={'class': 'tag-input'}))
    class Meta:
        model = Issue
        fields = ['issuename', 'description', 'tags_field']
        help_texts = {
            'issuename': "Enter the name of the issue.",
            'description': "Provide a detailed description of the issue.",
            'tags': "Enter tags related to the issue."
        }

    def __init__(self, *args, **kwargs):
        super(EditIssueForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')
    def save(self, commit=True):
        issue = super().save(commit=False)
        tag_names = self.cleaned_data.get('tags', '')
        if tag_names:
            tag_list = tag_names.split(',')
            tags = []
            for tag_name in tag_list:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                tags.append(tag)
            issue.tags.set(tags)
        if commit:
            issue.save()

class IssueFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', '--------')]+Issue.STATUS_CHOICES, 
        required=False, 
        help_text="Filter issues by status."
    )
    created_by = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        required=False, 
        help_text="Filter issues by the creator."
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(), 
        required=False, 
        help_text="Filter issues by company."
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(), 
        required=False, 
        help_text="Filter issues by product."
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(), 
        required=False, 
        help_text="Filter issues by tags.",
        widget=forms.SelectMultiple(attrs={'size': 5})  # Adjust size as needed
    )
    user_issues = forms.BooleanField(
        required=False, 
        help_text="Filter issues created by the logged-in user."
    )
    
class SupportQueryForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['type', 'message']
        help_texts = {
            'type': "Select the type of support query.",
            'message': "Enter your support message."
        }

    def __init__(self, *args, **kwargs):
        super(SupportQueryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

class HiringRequestForm(forms.ModelForm):
    class Meta:
        model = Hiring
        fields = ['name', 'url', 'options', 'description']
        help_texts = {
            'name': "Enter the name of the hiring request.",
            'url': "Enter the URL for the hiring request.",
            'options': "Select options for the hiring request.",
            'description': "Provide a detailed description of the hiring request."
        }

    def __init__(self, *args, **kwargs):
        super(HiringRequestForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['options', 'bool', 'comment']
        help_texts = {
            'options': "Select an option for the feedback.",
            'bool': "Indicate whether the feedback is positive or negative.",
            'comment': "Provide additional comments for the feedback."
        }

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

class EditFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['options', 'bool', 'comment']
        help_texts = {
            'options': "Select an option for the feedback.",
            'bool': "Indicate whether the feedback is positive or negative.",
            'comment': "Provide additional comments for the feedback."
        }

    def __init__(self, *args, **kwargs):
        super(EditFeedbackForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['description']
        help_texts = {
            'description': "Enter your comment here."
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

class HiringCommentForm(forms.ModelForm):
    class Meta:
        model = HiringComment
        fields = ['description']
        help_texts = {
            'description': "Enter your comment here."
        }

    def __init__(self, *args, **kwargs):
        super(HiringCommentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['options', 'bool', 'comment']
        help_texts = {
            'options': "Select an option for the feedback.",
            'bool': "Indicate whether the feedback is positive or negative.",
            'comment': "Provide additional comments for the feedback."
        }

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f'<span><span class="required-label">*</span>{field.label}</span>')
