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
    path('privateissues/',viewPrivateIssues, name='privateissues'),
    path('privateissues/<str:id>',getIssue, name='privateissues'),
    path('addcomment/',addComment, name='addcomment'),
    path('addfeedback/',addFeedback, name='addfeedback'),
    path('ajax/load-products/',load_products, name='load_products'),
    path('changepassword/', change_password, name='changepassword'),
    path('user/<str:id>',getUser,name='getuser'),
    path('profile/<str:id>',getProfile,name='getprofile'),
    path('editprofile/', editProfile, name='editprofile'),
    path('editissue/<uuid:issue_id>/', editIssue, name='editissue'),
    path('editfeedback/<uuid:feedback_id>/', editFeedback, name='editfeedback'),
    path('companydetails/<uuid:company_id>/', companyDetails, name='companydetails'),
    path('issue/<uuid:issue_id>/changestatus/', changeIssueStatus, name='changeissuestatus'),
    path('support/', supportForm, name='support'),
    path('hiring/',hiringForm, name='hiring'),
    path('supportlist/',supportList, name='supportlist'),
    path('hiringlist/',hiringList, name='hiringlist'),
    path('supportformsuccess/', supportFormSuccess, name='supportformsuccess'),
]
