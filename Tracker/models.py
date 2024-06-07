from django.db import models
import json
from django.contrib.auth.models import AbstractUser
import uuid
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
    username = models.CharField(max_length=255, unique=True)
    image=models.ImageField(upload_to='images',default="/images/Empty-image.jpg")
    password = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    enabled=models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users',null=True, blank=True)

    def __str__(self):
        return self.username

# Product model
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name

# Issue model
class Issue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('in_progress', 'In Progress'),
    ]
    
    issuename = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_issues')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='issues')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='issues', null=True, blank=True)
    tags = models.TextField()  # Store tags as a JSON list
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,default='open')
    viewcount = models.PositiveIntegerField(default=0)
    suggestioncount = models.PositiveIntegerField(default=0)
    commentcount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.issuename


# Comment model
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    description = models.TextField()

    def __str__(self):
        return f'Comment by {self.user.username} on {self.issue.issuename}'



# Feedback model
class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    description = models.TextField()
    disabled = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

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
