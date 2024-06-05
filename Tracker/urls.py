from django.urls import path
from .views import *
urlpatterns = [
    path('signup/', signUp, name='sign_up'),
    path('login/', loginView, name='login'),
    path('home/',home, name='home'),
    path('addproduct/',addProduct, name='add_product'),
    path('addissue/',addIssue, name='add_issue'),
    path('issues/<str:id>', getIssue, name='issue'),
    path('issues/', getAllIssues, name='issues'),

]
