from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse,JsonResponse
from rest_framework.response import Response
from django.contrib import messages
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import *
from .serializers import *
from django.db.models import Count,Q
import datetime
from django.core.paginator import Paginator
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
            if len(feed)>0:
                edit=True
        except:
            pass
        #data=IssueSerializer(object).data
        print(object.created_by,self.user,object.created_by.is_superuser)
        if object.created_by==self.user or self.user.is_superuser==True:
            value=True
        else:
            value=False
        form=FeedbackForm()

        return render(self,'DisplayIssue.html',{'issue':object,'edit':edit,'form':form,'pinnedcomments':pinnedcomments,'comments':comments,'feedback':feedback,'feedbackCount':len(feedback),'viewedby':viewedobjs,'value':value,'companyid':companyid,'companyuser':companyuser,'userid':self.user.id})
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'},status=status.HTTP_404_NOT_FOUND)

@login_required(login_url='/login/')
def getAllIssues(request):
    try:
        issues = Issue.objects.filter(private=False).order_by()
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

        issues = issues.annotate(
            option1_count=Count('feedbacks', filter=Q(feedbacks__options='option1')),
            option2_count=Count('feedbacks', filter=Q(feedbacks__options='option2')),
            option3_count=Count('feedbacks', filter=Q(feedbacks__options='option3')),
            bool_true_count=Count('feedbacks', filter=Q(feedbacks__bool=True)),
            bool_false_count=Count('feedbacks', filter=Q(feedbacks__bool=False))
        )

        paginator = Paginator(issues, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        print(page_obj)

        return render(request, 'Display.html', {
            'page_obj': page_obj,
            'filter_form': filter_form,
            'userid': request.user.id
        })
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'}, status=status.HTTP_404_NOT_FOUND)


def add_comment(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.user = request.user
            comment.save()
            return redirect(reverse('issue', kwargs={'id': issue_id}))
            
    else:
        form = CommentForm()
    return render(request, 'addcomment.html', {'form': form, 'issue': issue})

def add_hiring_comment(request, hiring_id):
    print("entered",hiring_id)
    hiring = Hiring.objects.get(id=hiring_id)
    print("hiring",hiring)
    if request.method == 'POST':
        form = HiringCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.hiring =hiring
            comment.user = request.user
            comment.save()
            return redirect('hirings')
    else:
        form = HiringCommentForm()
    return render(request, 'addhiringcomment.html', {'form': form, 'issue': hiring})

def add_feedback(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.issue = issue
            feedback.user = request.user
            feedback.save()
            return redirect(reverse('issue', kwargs={'id': issue_id}))
            return redirect('issue', id=issue.id)
    else:
        form = FeedbackForm()
    return render(request, 'addfeedback.html', {'form': form, 'issue': issue})
# @login_required(login_url='/login/')
# def editFeedback(request, feedback_id):
#     feedback = get_object_or_404(Feedback, id=feedback_id)
#     form = FeedbackForm(request.POST, instance=feedback)

#     if form.is_valid():
#         form.save()
#         return JsonResponse({'status': 'success', 'message': 'Feedback updated successfully.'})
#     else:
#         return JsonResponse({'status': 'error', 'errors': form.errors})

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
    companyid=None
    company=False
    try:
        companyid=request.user.company.id
        company=True
    except:
        pass
    issues_created = Issue.objects.filter(created_by=user,enabled=True)
    issues_count = issues_created.count()
    # feedback_count = len(Feedback.objects.filter(user=user,enabled=True))
    comment_count = issues_created.aggregate(total_comments=models.Sum('commentcount'))['total_comments'] or 0
    view_count = issues_created.aggregate(total_views=models.Sum('viewcount'))['total_views'] or 0

    context = {
        'user': user,
        'issues_count': issues_count,
        # 'feedback_count': feedback_count,
        'comment_count': comment_count,
        'view_count': view_count,
        'companyid':companyid,
        'company':company
    }
    return render(request, 'userprofile.html', context)


@login_required(login_url='login/')
def getProfile(request,id):
    user = get_object_or_404(User, id=id)
    print("user")
    #user=issue.created_by
    company=False
    try:
        companyid=request.user.company.id
        company=True
    except:
        companyid=None
    issues_created = Issue.objects.filter(created_by=user,enabled=True)
    issues_count = issues_created.count()
    # feedback_count = len(Feedback.objects.filter(user=user,enabled=True))
    comment_count = issues_created.aggregate(total_comments=models.Sum('commentcount'))['total_comments'] or 0
    view_count = issues_created.aggregate(total_views=models.Sum('viewcount'))['total_views'] or 0

    context = {
        'user': user,
        'issues_count': issues_count,
        'comment_count': comment_count,
        'view_count': view_count,
        'companyid':companyid,
        'company':company
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
    old_values = {
                'options': feed.options,
                'bool': feed.bool,
                'enabled': feed.enabled,
                'comment': feed.comment,
                'pinned': feed.pinned
            }
    if request.method == 'POST':
        form = EditFeedbackForm(request.POST, instance=feed)
        if form.is_valid():
            # Capture old values

            form.save()
            feed.refresh_from_db()
            new_values = {
                'options': feed.options,
                'bool': feed.bool,
                'enabled': feed.enabled,
                'comment': feed.comment,
                'pinned': feed.pinned
            }

            # Generate log entry
            changes = []
            for field in old_values:
                if old_values[field] != new_values[field]:
                    changes.append(f"{field} changed from '{old_values[field]}' to '{new_values[field]}'")

            log_entry = f"Feedback updated by {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}. Changes: {'; '.join(changes)}"

            # Create a log entry after the feedback is updated
            FeedbackLogs.objects.create(
                feedback=feed,
                old_values=json.dumps(old_values),
                new_values=json.dumps(new_values),
                timestamp=timezone.now(),
                log_entry=log_entry
            )

            messages.success(request, 'Feedback updated successfully')
            return redirect(reverse('issue', kwargs={'id': feed.issue.id}))  # Redirect to issue detail page after edit
    else:
        form = EditFeedbackForm(instance=feed)
    return render(request, 'editfeedback.html', {'form': form})


def companyDetails(request, company_id):
    context = {}
    company = get_object_or_404(Company, id=company_id)
    context['company'] = company
    
    try:
        users = User.objects.filter(company=company, companyuser=True, enabled=True)
        context['users'] = users
    except:
        context['users'] = None
    
    try:
        products = Product.objects.filter(company=company)
        context['products'] = products
    except:
        context['products'] = None

    try:
        issues = Issue.objects.filter(company=company)
        context['issues_count'] = issues.count()
        
        # Get status choices from the Issue model
        status_choices = dict(Issue.STATUS_CHOICES)
        context['status_choices'] = status_choices
        
        # Count issues per status
        status_counts = issues.values('status').annotate(count=Count('id'))
        context['status_counts'] = status_counts
        
        # Count issues per tag
        tag_counts = issues.values('tags').annotate(count=Count('id'))
        context['tag_counts'] = tag_counts
        
        context['issues'] = issues
        
        # Specific statistics for each product
        product_stats = []
        for product in products:
            product_issues = issues.filter(product=product)
            product_status_counts = product_issues.values('status').annotate(count=Count('id'))
            product_tags_counts = product_issues.values('tags').annotate(count=Count('id'))
            
            product_stat = {
                'product': product,
                'total_issues': product_issues.count(),
                'status_counts': {
                    status: product_issues.filter(status=status).count() for status in status_choices.keys()
                },
                # 'tag_counts':{
                #     tag: product_issues.filter(tags=tag).count() for tag in tag_counts
                # }
            }
            product_stats.append(product_stat)
        
        context['product_stats'] = product_stats
        
    except:
        context['issues'] = None
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
    hiring_objects = Hiring.objects.all().order_by('-created_at')
    hiringcomments=HiringComment.objects.all()
    
    return render(request, 'hiringlist.html', {'requests': hiring_objects, 'comments': hiringcomments})



def viewPrivateIssues(request):
    user=request.user
    try:
        privateissues=Issue.objects.filter(company=user.company,private=True)
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

        # data = IssueSerializer(issues, many=True).data
        return render(request, 'privateissue.html', {'data': privateissues, 'filter_form': filter_form,'userid':request.user.id,'user':user})
    except:
        return Response({'error': 'No Data Found'}, status=status.HTTP_404_NOT_FOUND)
    

def getLogs(request,id):
    feedback=Feedback.objects.get(id=id)
    logs=FeedbackLogs.objects.filter(feedback=feedback).order_by('timestamp')
    return render(request, 'feedbacklogs.html', {'logs': logs})
    
