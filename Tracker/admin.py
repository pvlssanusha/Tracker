from django.contrib import admin
from .models import *;
class IssueAdmin(admin.ModelAdmin):
    list_display = ('id','issuename','description','product','status','tags','created_by')
# Register your models here.
admin.site.register(User)
admin.site.register(Company)
admin.site.register(Issue,IssueAdmin)
admin.site.register(Product)
admin.site.register(Comment)
admin.site.register(Feedback)