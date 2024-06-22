from django.db import models
import json
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.postgres.fields import ArrayField
# Company model
class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    email = models.EmailField(max_length=255)
    bio = models.TextField()
    pic = models.ImageField(upload_to='company_pics/', null=True, blank=True)
    def __str__(self):
        return self.name

# User model
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    image=models.ImageField(upload_to='images',default="/images/Empty-image.jpg")
    password = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    companyuser=models.BooleanField(default=False)
    enabled=models.BooleanField(default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users',null=True, blank=True)

    def __str__(self):
        return self.username
    @property
    def custom_username(self):
        if self.is_staff:  # Assuming admin users are flagged with is_staff
            return f"{self.username} (Admin)"
        elif self.companyuser:
            return f"{self.username} (CompanyUser)"
        else:
            return self.username

# Product model
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255,blank=True,null=True)

    def __str__(self):
        return self.name
# Issue model
class Issue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('investigating', 'Investigating'),
        ('fixed', 'Fixed'),
        ('cannotfix','CannotFix')
    ]

    issuename = models.CharField(max_length=255)
    enabled=models.BooleanField(default=True)
    description = models.TextField()
    created_by = models.ForeignKey('User', on_delete=models.CASCADE,)
    company = models.ForeignKey('Company', on_delete=models.CASCADE,)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    tags = models.ManyToManyField('Tag')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,default='created')
    viewcount = models.PositiveIntegerField(default=0)
    feedbackcount = models.PositiveIntegerField(default=0)
    commentcount = models.PositiveIntegerField(default=0)
    private=models.BooleanField(default=False)
    pinned=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.issuename


# Comment model
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    enabled=models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    description = models.TextField()
    pinned=models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.issue.issuename}'



# Feedback model
class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CHOICES = [
        ('option1', 'option1'),
        ('option2', 'option2'),
        ('option3', 'option3'),
    ]
    options = models.CharField(max_length=100,choices=CHOICES)
    bool=models.BooleanField(default=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    enabled=models.BooleanField(default=True)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    pinned=models.BooleanField(default=False)

    def __str__(self):
        return f'Feedback by {self.user.username} on {self.issue.issuename}'

# ViewedBy model
class ViewedBy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vieweduser')
    timestamp = models.DateTimeField(auto_now_add=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='viewedissue')

    def __str__(self):
        return f'{self.user.username} viewed {self.issue.issuename}'


class Support(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    QUERY_TYPES = [
        ('query', 'Query'),
        ('feedback', 'Feedback'),
        ('technical_issue', 'Technical Issue'),
    ]

    type = models.CharField(max_length=20, choices=QUERY_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.created_at}"

class Hiring(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    CHOICES = [
        ('option1', 'option1'),
        ('option2', 'option2'),
        ('option3', 'option3'),
    ]
    name = models.CharField(max_length=100)
    url = models.URLField()
    options = models.CharField(max_length=100,choices=CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)
    timestamp= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.created_at}"
    
class HiringComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hiring = models.ForeignKey(Hiring, on_delete=models.CASCADE,)
    enabled=models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    description = models.TextField()
    pinned=models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.hiring.name}'
    
class FeedbackLogs(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)
    old_values = models.TextField(null=True,blank=True)
    new_values = models.TextField(null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    log_entry = models.TextField(null=True,blank=True)

class IssueStatusLog(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    oldstatus=models.TextField(null=True,blank=True)
    newstatus=models.TextField(null=True,blank=True)
    log_entry = models.TextField(null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


