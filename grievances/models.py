from django.db import models
from django.contrib.auth.models import AbstractUser, User, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import uuid
from .ai_utils import AIUtils, PriorityAssessor
from django.urls import reverse
from django.core.validators import MinLengthValidator

class CustomUser(AbstractUser):
    """Custom user model with additional fields"""
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_government_official = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True)
    
    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Status(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_name_display()

class Grievance(models.Model):
    CATEGORY_CHOICES = [
        ('infrastructure', 'Infrastructure'),
        ('sanitation', 'Sanitation'),
        ('safety', 'Safety'),
        ('education', 'Education'),
        ('health', 'Health'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='grievances/', blank=True, null=True)
    location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_grievances')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_grievances')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_anonymous = models.BooleanField(default=False)

    # AI-generated fields
    ai_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    ai_priority_confidence = models.FloatField(default=0.5)
    ai_sentiment_score = models.FloatField(default=0.0)
    ai_suggested_category = models.CharField(max_length=100, blank=True)
    ai_category_confidence = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_creator_display(self):
        """Return 'Anonymous' if the submission is anonymous, otherwise return the username"""
        return "Anonymous" if self.is_anonymous else self.created_by.username

    def analyze_with_ai(self):
        """Analyze the grievance using AI tools."""
        priority_assessor = PriorityAssessor()
        
        # Assess priority
        priority, confidence = priority_assessor.assess_priority(self.title, self.description)
        self.ai_priority = priority
        self.ai_priority_confidence = confidence
        
        # Calculate sentiment score
        self.ai_sentiment_score = priority_assessor._calculate_sentiment_score(f"{self.title} {self.description}")
        
        self.save()
    
    def get_similar_grievances(self, limit=5):
        """Get similar grievances using AI."""
        ai_utils = AIUtils()
        all_grievances = Grievance.objects.exclude(pk=self.pk).values_list('description', flat=True)
        current_grievance = f"{self.title} {self.description}"
        
        similar_grievances = ai_utils.find_similar_grievances(
            current_grievance,
            list(all_grievances),
            top_n=limit
        )
        
        return similar_grievances
    
    def get_ai_response_suggestion(self):
        """Get AI-generated response suggestion."""
        ai_utils = AIUtils()
        context = f"Category: {self.category}, Priority: {self.ai_priority}"
        return ai_utils.generate_response_suggestion(self.description, context)

class GrievanceUpdate(models.Model):
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='updates')
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    comment = models.TextField()
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Update for {self.grievance.title} - {self.status.name}"

class GrievanceAttachment(models.Model):
    grievance = models.ForeignKey(Grievance, related_name='attachments', on_delete=models.CASCADE)
    file = models.ImageField(upload_to='grievance_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.grievance.title}"

class ForumDiscussion(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(CustomUser, related_name='liked_discussions', blank=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('grievances:discussion_detail', args=[str(self.id)])

class ForumReply(models.Model):
    discussion = models.ForeignKey(ForumDiscussion, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(CustomUser, related_name='liked_replies', blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Forum replies'

    def __str__(self):
        return f'Reply by {self.created_by.username} on {self.created_at}'
