from django.contrib import admin
from .models import CustomUser, Grievance, Category, Status, GrievanceUpdate, GrievanceAttachment

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_government_official', 'department')
    list_filter = ('is_government_official', 'department')
    search_fields = ('username', 'email', 'department')

@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_by', 'created_at', 'ai_priority')
    list_filter = ('category', 'status', 'ai_priority')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('ai_priority', 'ai_priority_confidence', 'ai_sentiment_score', 'ai_suggested_category')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'created_at')
    search_fields = ('name', 'department')

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(GrievanceUpdate)
class GrievanceUpdateAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'status', 'updated_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('grievance__title', 'comment')

@admin.register(GrievanceAttachment)
class GrievanceAttachmentAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('grievance__title',)
