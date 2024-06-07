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
    path('ajax/load-products/',load_products, name='load_products'),
]
