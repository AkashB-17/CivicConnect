from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'grievances'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('submit/', views.submit_grievance, name='submit_grievance'),
    path('my-grievances/', views.my_grievances, name='my_grievances'),
    path('faq/', views.faq, name='faq'),
    path('grievance/<int:pk>/', views.grievance_detail, name='grievance_detail'),
    path('grievance/<int:pk>/update-status/', views.update_status, name='update_status'),
    
    # Password reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='grievances/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='grievances/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='grievances/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='grievances/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Forum URLs
    path('forum/', views.forum_home, name='forum_home'),
    path('forum/discussion/new/', views.create_discussion, name='create_discussion'),
    path('forum/discussion/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('forum/like/', views.toggle_like, name='toggle_like'),
] 