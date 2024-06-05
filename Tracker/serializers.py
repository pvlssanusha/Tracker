from rest_framework import serializers
from .models import *
from django.utils.translation import gettext as _


        
class IssueSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    company =  serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    class Meta:
        model = Issue
        fields = "__all__"
    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by.username else None 
    def get_company(self, obj):
        return obj.company.name if obj.company.name else None
    def get_product(self, obj):
        return obj.product.name if obj.product.name else None