from django.db import models
import json
from django.contrib.auth.models import AbstractUser

# Company model
class Company(models.Model):
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
    password = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users',null=True, blank=True)

    def __str__(self):
        return self.username

# Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name

# Issue model
class Issue(models.Model):
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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    viewcount = models.PositiveIntegerField(default=0)
    suggestioncount = models.PositiveIntegerField(default=0)
    commentcount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.issuename

    def set_tags(self, tag_list):
        self.tags = json.dumps(tag_list)

    def get_tags(self):
        return json.loads(self.tags)

# Comment model
class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    description = models.TextField()

    def __str__(self):
        return f'Comment by {self.user.username} on {self.issue.issuename}'

# Feedback model
class Feedback(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    description = models.TextField()
    disabled = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback by {self.user.username} on {self.issue.issuename}'

# ViewedBy model
class ViewedBy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_issues')
    timestamp = models.DateTimeField(auto_now_add=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='views')

    def __str__(self):
        return f'{self.user.username} viewed {self.issue.issuename}'
