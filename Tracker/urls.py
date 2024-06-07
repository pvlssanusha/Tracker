from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('signup/', signUp, name='signup'),
    path('login/', loginView, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('',home, name='home'),
    path('addproduct/',addProduct, name='addproduct'),
    path('addissue/',addIssue, name='addissue'),
    path('issues/<str:id>',getIssue, name='issue'),
    path('issues/', getAllIssues, name='issues'),
    path('addcomment/',addComment, name='addcomment'),
    path('addfeedback/',addFeedback, name='addfeedback'),
    path('ajax/load-products/',load_products, name='load_products'),
]
