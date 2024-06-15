from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse,JsonResponse
from rest_framework.response import Response
from django.contrib import messages
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.decorators import login_required
from .forms import *
from .serializers import *
from django.db.models import Count
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
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")

        form = IssueForm(request.POST, request.FILES)
        
        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user
            issue.save()
            return redirect('issues')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = IssueForm()
    
    return render(request, 'Issue.html', {'form': form, 'title': 'Register Issue'})

@login_required(login_url='/login/')
def getIssue(self,id):
    try:
        object=Issue.objects.get(id=id)
        companyid=object.company.id
        if self.user.company==object.company:
            companyuser=True
        else:
            companyuser=False
        try:
            view=ViewedBy.objects.get(user=self.user,issue=object)
        except:
            ViewedBy.objects.create(user=self.user,issue=object)
            object.viewcount+=1
        object.save()
        comments=None
        feedback=None
        try:
            comments=Comment.objects.filter(issue=object,enabled=True,pinned=False)
            pinnedcomments=Comment.objects.filter(issue=object,enabled=True,pinned=True)
        except:
            pass
        try:
            feedback=Feedback.objects.filter(issue=object,enabled=True)
        except:
            pass
        try:
            viewedobjs=ViewedBy.objects.filter(issue=object)
        except:
            pass
        edit=False
        try:
            feed=Feedback.objects.filter(issue=object,user=self.user)
            print(len(feed))
            if len(feed)>0:
                edit=True
        except:
            pass
        data=IssueSerializer(object).data
        value=object.created_by==self.user
        form=FeedbackForm()

        return render(self,'DisplayIssue.html',{'issue':data,'edit':edit,'form':form,'pinnedcomments':pinnedcomments,'comments':comments,'feedback':feedback,'viewedby':viewedobjs,'value':value,'companyid':companyid,'companyuser':companyuser,'userid':self.user.id})
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'},status=status.HTTP_404_NOT_FOUND)

@login_required(login_url='/login/')
def getAllIssues(request):
    try:
        issues = Issue.objects.all()
        filter_form = IssueFilterForm(request.GET)

        if filter_form.is_valid():
            status = filter_form.cleaned_data.get('status')
            created_by = filter_form.cleaned_data.get('created_by')
            company = filter_form.cleaned_data.get('company')
            product = filter_form.cleaned_data.get('product')
            tags = filter_form.cleaned_data.get('tags')

            if status:
                issues = issues.filter(status=status)
            if created_by:
                issues = issues.filter(created_by=created_by)
            if company:
                issues = issues.filter(company=company)
            if product:
                issues = issues.filter(product=product)
            if tags:
                issues = issues.filter(tags__icontains=tags)

        data = IssueSerializer(issues, many=True).data
        return render(request, 'Display.html', {'data': data, 'filter_form': filter_form})
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'}, status=status.HTTP_404_NOT_FOUND)

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
    issue_id = request.POST.get('issue_id')
    issue = get_object_or_404(Issue, id=issue_id)

    form = FeedbackForm(request.POST)

    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.issue = issue
        feedback.user = request.user  # Assuming user is logged in
        feedback.save()
        return JsonResponse({'status': 'success', 'message': 'Feedback added successfully.'})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors})

# Optionally, you may want to implement an edit_feedback view as well
@login_required(login_url='/login/')
def editFeedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    form = FeedbackForm(request.POST, instance=feedback)

    if form.is_valid():
        form.save()
        return JsonResponse({'status': 'success', 'message': 'Feedback updated successfully.'})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors})

def load_products(request):
    company_id = request.GET.get('company_id')
    products = Product.objects.filter(company_id=company_id).all()
    return JsonResponse(list(products.values('id', 'name')), safe=False)


@login_required(login_url='login/')
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important, to keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('issues')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'changepassword.html', {
        'form': form
    })

@login_required(login_url='login/')
def getUser(request,id):
    issue = get_object_or_404(Issue, id=id)
    user=issue.created_by
    companyid=request.user.company.id
    issues_created = Issue.objects.filter(created_by=user,enabled=True)
    issues_count = issues_created.count()
    suggestion_count = issues_created.aggregate(total_suggestions=models.Sum('suggestioncount'))['total_suggestions'] or 0
    comment_count = issues_created.aggregate(total_comments=models.Sum('commentcount'))['total_comments'] or 0
    view_count = issues_created.aggregate(total_views=models.Sum('viewcount'))['total_views'] or 0

    context = {
        'user': user,
        'issues_count': issues_count,
        'suggestion_count': suggestion_count,
        'comment_count': comment_count,
        'view_count': view_count,
        'companyid':companyid,
    }
    return render(request, 'userprofile.html', context)


@login_required(login_url='login/')
def getProfile(request,id):
    user = get_object_or_404(User, id=id)
    print("user")
    #user=issue.created_by
    try:
        companyid=request.user.company.id
    except:
        companyid=None
    issues_created = Issue.objects.filter(created_by=user,enabled=True)
    issues_count = issues_created.count()
    suggestion_count = issues_created.aggregate(total_suggestions=models.Sum('suggestioncount'))['total_suggestions'] or 0
    comment_count = issues_created.aggregate(total_comments=models.Sum('commentcount'))['total_comments'] or 0
    view_count = issues_created.aggregate(total_views=models.Sum('viewcount'))['total_views'] or 0

    context = {
        'user': user,
        'issues_count': issues_count,
        'suggestion_count': suggestion_count,
        'comment_count': comment_count,
        'view_count': view_count,
        'companyid':companyid,
    }
    return render(request, 'edituserprofile.html', context)


def editProfile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('issues')  # Redirect to profile page after saving
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'editprofile.html', {'form': form})

def editIssue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        form = EditIssueForm(request.POST, instance=issue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Issue updated successfully')
            return redirect(reverse('issue', kwargs={'id': issue_id}))  # Redirect to issue detail page after edit
    else:
        form = EditIssueForm(instance=issue)
    return render(request, 'editissue.html', {'form': form})

def editFeedback(request, feedback_id):
    feed = get_object_or_404(Feedback, id=feedback_id)
    if request.method == 'POST':
        form = EditFeedbackForm(request.POST, instance=feed)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feedback updated successfully')
            return redirect(reverse('issue', kwargs={'id': feed.issue.id}))  # Redirect to issue detail page after edit
    else:
        form = EditFeedbackForm(instance=feed)
    return render(request, 'editfeedback.html', {'form': form})


def companyDetails(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    users = User.objects.filter(company=company, companyuser=True, enabled=True)
    products = Product.objects.filter(company=company)
    issues = company.issues.all()

    # Get status choices from the Issue model (assuming it's a field named status_choices)
    status_choices = dict(Issue.STATUS_CHOICES)

    # Count issues per status
    status_counts = issues.values('status').annotate(count=Count('id'))

    # Count issues per tag
    tag_counts = issues.values('tags').annotate(count=Count('id'))

    context = {
        'company': company,
        'users': users,
        'issues': issues,
        'issues_count': issues.count(),
        'products': products,
        'status_counts': status_counts,  # This provides per-status count
        'tag_counts': tag_counts,  # This provides per-tag count
        'status_choices': status_choices,  # Assuming these are available in your Issue model
    }
    
    return render(request, 'companydetails.html', context)



def changeIssueStatus(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == 'POST':
        form = IssueStatusForm(request.POST, instance=issue)
        if form.is_valid():
            form.save()
            return redirect(reverse('issue', args=[issue_id]))  # Redirect to the issue details page
    else:
        form = IssueStatusForm(instance=issue)

    context = {
        'form': form,
        'issue': issue,
    }

    return render(request, 'changeissuestatus.html', context)



def supportForm(request):
    if request.method == 'POST':
        form = SupportQueryForm(request.POST)
        if form.is_valid():
            support=form.save(commit=False)
            support.user=request.user
            support.save()

            return redirect('supportformsuccess')  # Redirect to a success page
    else:
        form = SupportQueryForm()
    
    return render(request, 'supportform.html', {'form': form})

def supportFormSuccess(request):
    return render(request, 'supportformsuccess.html')

def hiringForm(request):
    if request.method == 'POST':
        form = HiringRequestForm(request.POST)
        if form.is_valid():
            hiring=form.save(commit=False)
            hiring.user=request.user
            hiring.save()
            
            return redirect('supportformsuccess')  # Redirect to a success page
    else:
        form = HiringRequestForm()
    
    return render(request, 'hiringform.html', {'form': form})

def supportList(request):
    queries = Support.objects.all().order_by('-created_at')
    return render(request, 'supportlist.html', {'queries': queries})

def hiringList(request):
    requests = Hiring.objects.all().order_by('-created_at')
    return render(request, 'hiringlist.html', {'requests': requests})