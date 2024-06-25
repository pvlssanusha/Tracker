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
def save_tags(request, issue):
    # tags = form.cleaned_data['tags_field']
    # tag_names = form.cleaned_data['tags_field']
    # tag_names = [tag.strip() for tag in tags.split(',') if tag.strip()]
    tag_names = json.loads(request.POST['tags_field'])
    issue.tags.clear()
    for tag_name in tag_names:
        try:
            tag= Tag.objects.get(name=tag_name['value'])
        except:
            tag= Tag.objects.create(name=tag_name['value'],user=request.user)
        issue.tags.add(tag)   

def get_taglist():
    taglist = '['
    total = Tag.objects.all().count()
    i = 0
    for tag in Tag.objects.all():
        description = tag.description
        if not description:
            description = tag.name
        taglist = taglist + '{ value:"' + tag.name + '", full:"' + description + '"}'
        i = i + 1
        if i < total:
            taglist = taglist + ','
    taglist = taglist + ']'
    return taglist


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
            save_tags(request, issue)
            messages.success(request,'Issue Created Successfully')
            return redirect('issues')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = IssueForm()

    return render(request, 'Issue.html', {'form': form, 'title': 'Register Issue','taglist': get_taglist()})

@login_required(login_url='/login/')
def getIssue(self,id):
    try:
        object=Issue.objects.get(id=id)
        companyid=object.company.id
        companyuser=False
        if self.user.company==object.company:
            if self.user.companyuser:
                companyuser=True
        try:
            view=ViewedBy.objects.get(user=self.user,issue=object)
        except:
            ViewedBy.objects.create(user=self.user,issue=object)
            # if self.user.companyuser:
            #         log_entry="Issue is Viewed By Company"
            #         IssueStatusLog.objects.create(
            #             oldstatus=object.status,
            #             newstatus="Viewed",
            #             issue=object,
            #             user=self.user,
            #             timestamp=timezone.now(),
            #             log_entry=log_entry
            #         )
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
            feed=Feedback.objects.filter(issue=object,user=self.user,enabled=True)
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
        tags=object.tags.all()

        return render(self,'DisplayIssue.html',{'issue':object,'tags':tags,'edit':edit,'form':form,'pinnedcomments':pinnedcomments,'comments':comments,'feedback':feedback,'feedbackCount':len(feedback),'viewedby':viewedobjs,'value':value,'companyid':companyid,'companyuser':companyuser,'userid':self.user.id})
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'},status=status.HTTP_404_NOT_FOUND)
@login_required(login_url='/login/')
def getAllIssues(request):
    try:
        issues = Issue.objects.filter(private=False, enabled=True).order_by('-created_at')
        filter_form = IssueFilterForm(request.GET)

        if filter_form.is_valid():
            status = filter_form.cleaned_data.get('status')
            created_by = filter_form.cleaned_data.get('created_by')
            company = filter_form.cleaned_data.get('company')
            product = filter_form.cleaned_data.get('product')
            tags = filter_form.cleaned_data.get('tags')
            user_issues = filter_form.cleaned_data.get('user_issues')

            if status:
                issues = issues.filter(status=status).order_by('-created_at')
            if created_by:
                issues = issues.filter(created_by=created_by).order_by('-created_at')
            if company:
                issues = issues.filter(company=company).order_by('-created_at')
            if product:
                issues = issues.filter(product=product).order_by('-created_at')
            if tags:
                issues = issues.filter(tags__in=tags).distinct().order_by('-created_at')
            if user_issues:
                issues = issues.filter(created_by=request.user).order_by('-created_at')

        issues = issues.annotate(
            option1_count=Count('feedbacks', filter=Q(feedbacks__options='option1')),
            option2_count=Count('feedbacks', filter=Q(feedbacks__options='option2')),
            option3_count=Count('feedbacks', filter=Q(feedbacks__options='option3')),
            bool_true_count=Count('feedbacks', filter=Q(feedbacks__bool=True)),
            bool_false_count=Count('feedbacks', filter=Q(feedbacks__bool=False))
        )

        pinned_issues = issues.filter(pinned=True)
        non_pinned_issues = issues.filter(pinned=False)

        combined_issues = list(pinned_issues) + list(non_pinned_issues)
        paginator = Paginator(combined_issues, 5) 

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        usercompanyid = None
        if request.user.companyuser:
            usercompanyid = request.user.company.id

        return render(request, 'Display.html', {
            'page_obj': page_obj,
            'filter_form': filter_form,
            'user': request.user,
            'usercompanyid': usercompanyid,
            'userid': request.user.id
        })
    except Issue.DoesNotExist:
        return Response({'error': 'No Data Found'}, status=status.HTTP_404_NOT_FOUND)


def viewPrivateIssues(request):
    user=request.user
    try:
        issues=Issue.objects.filter(company=user.company,private=True,enabled=True)
        print(issues,user.company)
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
                issues = issues.filter(tags__in=filter_form.cleaned_data['tags']).distinct()
            
            paginator = Paginator(issues, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            print(page_obj)
            usercompanyid=None 
            if request.user.companyuser:
                user=request.user
                print(user)
                usercompanyid=user.company.id
            print(usercompanyid)

        # data = IssueSerializer(issues, many=True).data
        return render(request, 'privateissue.html', {'page_obj': page_obj, 'filter_form': filter_form,'userid':request.user.id,'user':user,'usercompanyid':usercompanyid})
    except:
        return Response({'error': 'No Data Found'}, status=status.HTTP_404_NOT_FOUND)
    
def viewAdminPrivateIssues(request):
    user=request.user
    try:
        issues=Issue.objects.filter(private=True,enabled=True)
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
                issues = issues.filter(tags=tags)
            
            paginator = Paginator(issues, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            print(page_obj)
            usercompanyid=None 
            if request.user.companyuser:
                user=request.user
                print(user)
                usercompanyid=user.company.id
            print(usercompanyid)

        # data = IssueSerializer(issues, many=True).data
        return render(request, 'adminprivateissue.html', {'page_obj': page_obj, 'filter_form': filter_form,'userid':request.user.id,'user':user,'usercompanyid':usercompanyid})
    except:
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
    try:
        feed=Feedback.objects.get(issue=issue,user=request.user)
        print("feedback is already there")
        if request.method == 'POST':
            form=EditFeedbackForm(request.POST,instance=feed)
            old_values = {
                'options': feed.options,
                'bool': feed.bool,
                'enabled': feed.enabled,
                'comment': feed.comment,
                'pinned': feed.pinned
            }
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

            form.save()
            return redirect(reverse('issue', kwargs={'id': issue_id}))
        else:
            form=EditFeedbackForm(instance=feed)
            
    except:
        form = FeedbackForm()
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.issue = issue
            feedback.user = request.user
            feedback.save()
            return redirect(reverse('issue', kwargs={'id': issue_id}))
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
    print("company_id",company_id)
    if company_id !="":
        products = Product.objects.filter(company_id=company_id).all()
        return JsonResponse(list(products.values('id', 'name')), safe=False)
    return JsonResponse({},safe=False)

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
        if request.user.companyuser:
            company=True
    except:
        pass
    issues_created = Issue.objects.filter(created_by=user,enabled=True)
    issues_count = issues_created.count()
    feedback_count = len(Feedback.objects.filter(user=user))
    comment_count = len(Comment.objects.filter(user=user))
    view_count = len(ViewedBy.objects.filter(user=user))
    tags_created=len(Tag.objects.filter(user=user))
    tags=Tag.objects.filter(user=user)
    context = {
        'user': user,
        'tags':tags,
        'tags_created':tags_created,
        'issues_count': issues_count,
        'feedbacks_given': feedback_count,
        'comments_created': comment_count,
        'issues_viewed': view_count,
        'companyid':companyid,
        'company':company
    }
    return render(request, 'userprofile.html', context)


@login_required(login_url='login/')
def getProfile(request,id):
    user = get_object_or_404(User, id=id)
    print("user",user)
    #user=issue.created_by
    company=False
    try:
        companyid=request.user.company.id
        if request.user.companyuser:
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
            save_tags(request,issue)
            messages.success(request, 'Issue updated successfully')
            return redirect(reverse('issue', kwargs={'id': issue_id}))  # Redirect to issue detail page after edit
    else:
        form = EditIssueForm(instance=issue)
        form.fields['tags_field'].initial = ','.join([tag.name for tag in issue.tags.all()])
    return render(request, 'editissue.html', {'form': form,'taglist':get_taglist()})

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
    except User.DoesNotExist:
        context['users'] = None
    
    try:
        products = Product.objects.filter(company=company)
        context['products'] = products
    except Product.DoesNotExist:
        context['products'] = None

    try:
        issues = Issue.objects.filter(company=company, enabled=True)
        context['issues_count'] = issues.count()
        
        # Get status choices from the Issue model
        status_choices = dict(Issue.STATUS_CHOICES)
        context['status_choices'] = status_choices
        
        # Count issues per status
        status_counts = issues.values('status').annotate(count=Count('id'))
        context['status_counts'] = status_counts
        
        # Count issues per tag for the entire company
        tag_counts = Tag.objects.filter(issue__in=issues).annotate(count=Count('id')).values('name', 'count')
        tag_counts_dict = {tag['name']: tag['count'] for tag in tag_counts}
        context['tag_counts'] = tag_counts_dict
        
        context['issues'] = issues
        
        # Specific statistics for each product
        product_stats = []
        for product in products:
            product_issues = issues.filter(product=product)
            
            # Count tags for issues related to this product
            product_tag_counts = Tag.objects.filter(issue__in=product_issues).annotate(count=Count('id')).values('name', 'count')
            product_tag_counts_dict = {tag['name']: tag['count'] for tag in product_tag_counts}
            
            product_stat = {
                'product': product,
                'total_issues': product_issues.count(),
                'status_counts': {
                    status: product_issues.filter(status=status).count() for status in status_choices.keys()
                },
                'tag_counts': product_tag_counts_dict  # Tag counts specific to this product
            }
            product_stats.append(product_stat)
        
        context['product_stats'] = product_stats
        
    except Issue.DoesNotExist:
        context['issues'] = None
    
    return render(request, 'companydetails.html', context)


def productStatsView(request, product_id):
    # Get the product
    product = get_object_or_404(Product, id=product_id)
    
    # Filter issues related to this product
    product_issues = Issue.objects.filter(product=product)
    
    # Count tags for issues related to this product
    product_tag_counts = Tag.objects.filter(issue__in=product_issues).annotate(count=Count('id')).values('name', 'count')
    product_tag_counts_dict = {tag['name']: tag['count'] for tag in product_tag_counts}
    
    # Status choices (assuming you have defined these in your Issue model)
    status_choices = Issue.STATUS_CHOICES
    
    # Calculate the stats
    product_stat = {
        'product': product,
        'total_issues': product_issues.count(),
        'status_counts': {
            status: product_issues.filter(status=status).count() for status, _ in status_choices
        },
        'tag_counts': product_tag_counts_dict  # Tag counts specific to this product
    }
    
    context = {
        'product_stat': product_stat
    }
    
    return render(request, 'productstats.html', context)



def changeIssueStatus(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    oldstatus= issue.status
    if request.method == 'POST':
        form = IssueStatusForm(request.POST, instance=issue)
        if form.is_valid():
            form.save()
            newstatus=form.cleaned_data['status']
            user=request.user
            log_entry = f"Issue Status updated by {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} from {oldstatus} to {newstatus}"
            IssueStatusLog.objects.create(
                oldstatus=oldstatus,
                newstatus=newstatus,
                issue=issue,
                user=user,
                timestamp=timezone.now(),
                log_entry=log_entry
            )
            messages.success(request, 'Issue Status updated successfully')

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
    all_hirings = Hiring.objects.all().order_by('-created_at')
    hiringcomments = HiringComment.objects.all()

    # Separate pinned and non-pinned items
    pinned_hirings = [hiring for hiring in all_hirings if hiring.pinned]
    non_pinned_hirings = [hiring for hiring in all_hirings if not hiring.pinned]

    pinned_comments = [comment for comment in hiringcomments if comment.pinned]
    non_pinned_comments = [comment for comment in hiringcomments if not  comment.pinned]
    # Combine pinned and non-pinned hirings for pagination
    combined_hirings = pinned_hirings + non_pinned_hirings
    hiringcomments=pinned_comments + non_pinned_comments
    paginator = Paginator(combined_hirings, 5)  # Show 5 hiring requests per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hiringlist.html', {
        'pinned_hirings': pinned_hirings,
        'page_obj': page_obj,
        'comments': hiringcomments
    })




def getLogs(request,id):
    feedback=Feedback.objects.get(id=id)
    logs=FeedbackLogs.objects.filter(feedback=feedback).order_by('timestamp')
    return render(request, 'feedbacklogs.html', {'logs': logs})

def getIssueLogs(request,id):
    issue=Issue.objects.get(id=id)
    logs=IssueStatusLog.objects.filter(issue=issue).order_by('timestamp')
    return render(request, 'issuestatuslog.html', {'logs': logs})


def reportIssue(request,id):
    issue=Issue.objects.get(id=id)
    if request.method == 'POST':
        form = ReportIssueForm(request.POST)
        if form.is_valid():
            report=form.save(commit=False)
            report.user=request.user
            report.issue=issue
            report.save()
            return redirect(reverse('issue', args=[id]))
    else:
        form = ReportIssueForm()
        return render(request,'reportissue.html', {'form': form})
    
def reportComment(request,id):
    comment=Comment.objects.get(id=id)
    issue=comment.issue.id
    if request.method == 'POST':
        form = ReportCommentForm(request.POST)
        if form.is_valid():
            report=form.save(commit=False)
            report.user=request.user
            report.comment=comment
            print("error")
            report.save()
            return redirect(reverse('issue', args=[issue]))
    else:
        form = ReportCommentForm()
        return render(request,'reportcomment.html', {'form': form})
    
def reportHiringComment(request,id):
    comment=HiringComment.objects.get(id=id)
    issue=comment.hiring.id
    if request.method == 'POST':
        form = ReportHiringCommentForm(request.POST)
        if form.is_valid():
            report=form.save(commit=False)
            report.user=request.user
            report.comment=comment
            print("error")
            report.save()
            return redirect(reverse('hirings'))
    else:
        form = ReportCommentForm()
        return render(request,'reportcomment.html', {'form': form})
    
def reportFeedback(request,id):
    feedback=Feedback.objects.get(id=id)
    issue=feedback.issue.id
    if request.method == 'POST':
        form = ReportFeedbackForm(request.POST)
        if form.is_valid():
            report=form.save(commit=False)
            report.user=request.user
            report.feedback=feedback
            report.save()
            return redirect(reverse('issue', args=[issue]))
    else:
        form = ReportCommentForm()
        return render(request,'reportfeedback.html', {'form': form})
         



    
