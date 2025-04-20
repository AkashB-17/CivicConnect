import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Grievance, Status, GrievanceUpdate, GrievanceAttachment, ForumDiscussion, ForumReply, CustomUser
from .forms import (
    SearchForm, GrievanceForm, CustomUserCreationForm, CustomAuthenticationForm,
    ForumDiscussionForm, ForumReplyForm
)
from .ai_utils import SearchEnhancer

logger = logging.getLogger(__name__)

def home(request):
    form = SearchForm(request.GET or None)
    grievances = Grievance.objects.all().order_by('-created_at')
    enhanced_terms = None

    if request.GET.get('query') and not request.user.is_authenticated:
        messages.info(request, 'Please log in to use the search functionality.')
        return redirect('grievances:login')

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            try:
                search_enhancer = SearchEnhancer()
                enhanced_terms = search_enhancer.enhance_search_query(query)

                q_objects = Q()
                for term in enhanced_terms:
                    q_objects |= Q(title__icontains=term) | Q(description__icontains=term)

                filtered = grievances.filter(q_objects)
                scored = [
                    (g, search_enhancer.calculate_relevance_score(g.title, enhanced_terms) * 2 +
                        search_enhancer.calculate_relevance_score(g.description, enhanced_terms))
                    for g in filtered
                ]
                scored.sort(key=lambda x: (-x[1], -x[0].created_at.timestamp()))
                grievances = [g[0] for g in scored]
            except Exception as e:
                logger.error(f"Search enhancement failed: {e}")
                messages.warning(request, 'Search could not be processed at this time.')

    paginator = Paginator(grievances, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'grievances/home.html', {
        'form': form,
        'page_obj': page_obj,
        'recent_grievances': grievances[:5],
        'search_query': request.GET.get('query', ''),
        'enhanced_terms': enhanced_terms,
        'is_search': bool(request.GET.get('query')),
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.is_active = True
                
                # Check if this is an admin registration
                if request.POST.get('is_admin') == '1':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    messages.success(request, 'Administrator account created successfully! You can now log in to the admin interface.')
                    return redirect('/admin/')
                
                user.save()
                messages.success(request, 'Registration successful! You can now log in.')
                return redirect('grievances:login')
            except Exception as e:
                logger.error(f"Registration error: {e}")
                messages.error(request, 'An error occurred during registration. Please try again.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'grievances/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('grievances:home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'grievances/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('grievances:home')

@login_required(login_url='grievances:register')
def submit_grievance(request):
    if request.method == 'POST':
        form = GrievanceForm(request.POST, request.FILES)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.created_by = request.user
            grievance.category = 'other'
            grievance.save()

            for file in request.FILES.getlist('attachments'):
                if file.content_type.startswith('image/'):
                    GrievanceAttachment.objects.create(grievance=grievance, file=file)

            try:
                grievance.analyze_with_ai()
                messages.success(request, 'Grievance submitted successfully with AI analysis!')
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                messages.warning(request, 'Grievance submitted, but AI analysis failed.')

            return redirect('grievances:grievance_detail', pk=grievance.pk)
    else:
        form = GrievanceForm()
    return render(request, 'grievances/submit_grievance.html', {'form': form})

@login_required
def my_grievances(request):
    grievances = Grievance.objects.filter(created_by=request.user).order_by('-created_at')
    paginator = Paginator(grievances, 10)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    return render(request, 'grievances/my_grievances.html', {'page_obj': page_obj})

@login_required
def grievance_detail(request, pk):
    try:
        grievance = get_object_or_404(Grievance, pk=pk)
        updates = GrievanceUpdate.objects.filter(grievance=grievance).order_by('-created_at')
        similar = grievance.get_similar_grievances(limit=5)
        ai_response = grievance.get_ai_response_suggestion() if request.user.is_staff else None
        status_choices = Status.STATUS_CHOICES

        return render(request, 'grievances/grievance_detail.html', {
            'grievance': grievance,
            'updates': updates,
            'similar_grievances': similar,
            'ai_response': ai_response,
            'status_choices': status_choices
        })
    except Exception as e:
        logger.error(f"Error loading grievance detail: {e}")
        messages.error(request, 'Could not load grievance details.')
        return redirect('grievances:home')

@login_required
def update_status(request, pk):
    if not request.user.is_government_official:
        messages.error(request, 'You do not have permission to update status.')
        return redirect('grievances:grievance_detail', pk=pk)

    grievance = get_object_or_404(Grievance, pk=pk)
    if request.method == 'POST':
        status_name = request.POST.get('status')
        assigned_to_id = request.POST.get('assigned_to')
        comment = request.POST.get('comment')
        try:
            status = Status.objects.get(name=status_name)
            grievance.status = status
            if assigned_to_id:
                grievance.assigned_to = CustomUser.objects.get(id=assigned_to_id)
            grievance.save()
            GrievanceUpdate.objects.create(grievance=grievance, status=status, comment=comment, updated_by=request.user)
            messages.success(request, 'Status updated successfully!')
        except Exception as e:
            logger.error(f"Status update error: {e}")
            messages.error(request, 'Error updating status.')
    return redirect('grievances:grievance_detail', pk=pk)

def faq(request):
    return render(request, 'grievances/faq.html')

@login_required
def forum_home(request):
    discussions = ForumDiscussion.objects.all().order_by('-created_at')
    paginator = Paginator(discussions, 10)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    return render(request, 'grievances/forum/forum_home.html', {
        'discussions': page_obj,
        'form': ForumDiscussionForm()
    })

@login_required
def discussion_detail(request, discussion_id):
    discussion = get_object_or_404(ForumDiscussion, id=discussion_id)
    replies = discussion.replies.all().order_by('created_at')
    if request.method == 'POST':
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.discussion = discussion
            reply.created_by = request.user
            reply.save()
            messages.success(request, 'Your reply has been posted successfully.')
            return redirect('grievances:discussion_detail', discussion_id=discussion.id)
        else:
            messages.error(request, 'There was an error posting your reply.')
    else:
        form = ForumReplyForm()
    return render(request, 'grievances/discussion_detail.html', {
        'discussion': discussion,
        'replies': replies,
        'form': form
    })

@login_required
def create_discussion(request):
    if request.method == 'POST':
        form = ForumDiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.created_by = request.user
            discussion.save()
            messages.success(request, 'Discussion created successfully!')
            return redirect('grievances:discussion_detail', discussion_id=discussion.id)
        messages.error(request, 'There was an error creating your discussion.')
    else:
        form = ForumDiscussionForm()
    return render(request, 'grievances/forum/create_discussion.html', {'form': form})

@login_required
@require_POST
def add_reply(request, discussion_id):
    discussion = get_object_or_404(ForumDiscussion, id=discussion_id)
    form = ForumReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.discussion = discussion
        reply.created_by = request.user
        reply.save()
        return JsonResponse({
            'success': True,
            'reply': {
                'content': reply.content,
                'user': reply.created_by.username,
                'created_at': reply.created_at.strftime('%B %d, %Y, %I:%M %p')
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
@require_POST
def toggle_like(request):
    content_type = request.POST.get('type')
    object_id = request.POST.get('id')
    try:
        obj = ForumDiscussion.objects.get(pk=object_id) if content_type == 'discussion' \
            else ForumReply.objects.get(pk=object_id)

        if request.user in obj.likes.all():
            obj.likes.remove(request.user)
            liked = False
        else:
            obj.likes.add(request.user)
            liked = True

        return JsonResponse({'liked': liked, 'likes_count': obj.likes.count()})
    except Exception as e:
        logger.error(f"Toggle like error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
