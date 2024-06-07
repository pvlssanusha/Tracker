from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse,JsonResponse
from rest_framework.response import Response
from django.contrib import messages
from rest_framework import status
from django.contrib.auth.decorators import login_required
from .forms import *
from .serializers import *
import datetime
def signUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            email = form.cleaned_data.get('email')
            company = form.cleaned_data.get('company')
            if not username or not firstname or not lastname or not email:
                error_message = "Please fill in all required fields."
                return render(request, 'sign_up.html', {'form': form, 'error_message': error_message})
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
                return redirect('issues')
            else:
                messages.error(request, 'Account does not exist. Please sign in.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title': 'Log in'})

def home(request):
    return render(request, 'home.html')

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def addIssue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue=form.save(commit=False)
            issue.created_by=request.user
            issue.save()
            messages.success(request, 'Issue Registered successfully')
            return HttpResponse({'Issue Registered successfully': True})
        else:
            messages.error(request, 'Issue Not Registered ')
            return  HttpResponse({'Issue Not Registered': True})
    else:
        form=IssueForm()
        return render(request, 'Issue.html', {'form': form, 'title': 'Register Issue'})

@login_required(login_url='/login/')
def getIssue(self,id):
    try:
        object=Issue.objects.get(id=id)
        try:
            view=ViewedBy.objects.get(user=self.user,issue=object)
        except:
            ViewedBy.objects.create(user=self.user,issue=object)
            object.viewcount+=1
        object.save()
        comments=None
        feedback=None
        try:
            comments=Comment.objects.filter(issue=object)
        except:
            pass
        try:
            feedback=Feedback.objects.filter(issue=object)
        except:
            pass
        try:
            viewedobjs=ViewedBy.objects.filter(user=self.user,issue=object)
        except:
            pass
        data=IssueSerializer(object).data
        return render(self,'DisplayIssue.html',{'issue':data,'comments':comments,'feedback':feedback,'viewedby':viewedobjs})
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'},status=status.HTTP_404_NOT_FOUND)

@login_required(login_url='/login/')
def getAllIssues(self):
    try:
        object=Issue.objects.all()
        data=IssueSerializer(object,many=True).data
        print(data,"data")
        return render(self,'Display.html',{'data':data})
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'},status=status.HTTP_404_NOT_FOUND)

@login_required(login_url='/login/')
def addComment(request):
    if request.method == 'POST':
        issue_id=request.POST.get('issue_id')
        issue=Issue.objects.get(id=issue_id)
        comment=request.POST.get('comment')
        Comment.objects.create(issue=issue, user=request.user, description=comment)
        return redirect('issue', id=issue.id)

@login_required(login_url='/login/')
def addFeedback(request):
    if request.method == 'POST':
        print(request.POST)
        issue_id=request.POST.get('issue_id')
        issue=Issue.objects.get(id=issue_id)
        feedback=request.POST.get('feedback')
        Feedback.objects.create(issue=issue, user=request.user, description=feedback,timestamp=datetime.datetime.now())
        return redirect('issue', id=issue.id)

def load_products(request):
    company_id = request.GET.get('company_id')
    products = Product.objects.filter(company_id=company_id).all()
    return JsonResponse(list(products.values('id', 'name')), safe=False)
