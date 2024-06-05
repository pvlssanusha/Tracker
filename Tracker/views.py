from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from rest_framework.response import Response
from django.contrib import messages
from rest_framework import status
from .forms import *
from .serializers import *
def signUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Accessing individual cleaned data fields
            username = form.cleaned_data.get('username')
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            email = form.cleaned_data.get('email')
            company = form.cleaned_data.get('company')

            # Check if any required fields are empty
            if not username or not firstname or not lastname or not email:
                error_message = "Please fill in all required fields."
                return render(request, 'sign_up.html', {'form': form, 'error_message': error_message})

            # If all required fields are filled, save the form
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def loginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Account does not exist. Please sign in.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title': 'Log in'})

def home(request):
    return render(request, 'home.html')


def addProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully')
            return HttpResponse({'Product Added Successfully': True})
        else:
            messages.error(request, 'Product not added')
    else:
        form=ProductForm()
        return render(request, 'Product.html', {'form': form, 'title': 'Add Product'})
    
def addIssue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Issue Registered successfully')
            # return render('home.html')
            return HttpResponse({'Issue Registered successfully': True})
        else:
            messages.error(request, 'Issue Not Registered ')
            return  HttpResponse({'Issue Not Registered': True})
    else:
        form=IssueForm()
        return render(request, 'Issue.html', {'form': form, 'title': 'Register Issue'})
    
def getIssue(self,id):
    try:
        object=Issue.objects.get(id=id)
        data=IssueSerializer(object).data
        #return Response({'data':IssueSerializer(object).data},status=status.HTTP_200_OK)
        return render(self,'DisplayIssue.html',{'issue':data})
    
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'},status=status.HTTP_404_NOT_FOUND)
def getAllIssues(self):
    try:
        object=Issue.objects.all()
        data=IssueSerializer(object,many=True).data
        print(data,"data")
        return render(self,'Display.html',{'data':data})
    
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'},status=status.HTTP_404_NOT_FOUND)

