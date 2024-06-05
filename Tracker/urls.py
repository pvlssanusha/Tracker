from django.urls import path
from .views import *
urlpatterns = [
    path('signup/', signUp, name='signup'),
    path('login/', loginView, name='login'),
    path('home/',home, name='home'),
    path('addproduct/',addProduct, name='addproduct'),
    path('addissue/',addIssue, name='addissue'),
    path('issues/<str:id>',getIssue, name='issue'),
    path('issues/', getAllIssues, name='issues'),
    path('addcomment/',addComment, name='addcomment'),
    path('addfeedback/',addFeedback, name='addfeedback'),

]
