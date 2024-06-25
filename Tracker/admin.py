from django.contrib import admin
from .models import *;
class IssueAdmin(admin.ModelAdmin):
    list_display = ('id','issuename','description','product','status','created_by','company')
class ViewedByAdmin(admin.ModelAdmin):
    list_display=('id','timestamp','user','issue',)

class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username','email','password')
# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(Company)
admin.site.register(Tag)
admin.site.register(FeedbackLogs)
admin.site.register(HiringComment)
admin.site.register(Issue,IssueAdmin)
admin.site.register(Product)
admin.site.register(Comment)
admin.site.register(Feedback)
admin.site.register(Support)
admin.site.register(Hiring)
admin.site.register(IssueStatusLog)
admin.site.register(ReportFeedback)
admin.site.register(ReportHiringComment)
admin.site.register(ReportComment)
admin.site.register(ReportIssue)
admin.site.register(ViewedBy,ViewedByAdmin)