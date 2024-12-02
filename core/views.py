from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum
import requests
import json

from .models import UserProfile, Quest, Goal, Achievement, CommunityPost, UserQuest
from .forms import (
    UserRegistrationForm, UserProfileForm, QuestForm,
    GoalForm, CommunityPostForm, UserSettingsForm, UserProfileSettingsForm, 
    UserProfileEditForm, CommentForm, ContactForm
)
from .services.ai_service import AIService

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            login(request, user)
            messages.success(request, 'Welcome to Solo Leveling System!')
            return redirect('personality_quiz')
    else:
        form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'core/register.html', {
        'form': form,
        'profile_form': profile_form
    })

@login_required
def personality_quiz(request):
    if request.method == 'POST':
        # Process personality quiz answers
        answers = request.POST.dict()
        personality_result = analyze_personality(answers)
        
        # Update user profile with personality traits
        profile = request.user.userprofile
        profile.personality_type = personality_result['type']
        profile.strengths = personality_result['strengths']
        profile.weaknesses = personality_result['weaknesses']
        profile.save()
        
        messages.success(request, f'Your personality type: {personality_result["type"]}')
        return redirect('dashboard')
    
    return render(request, 'core/personality_quiz.html')

@login_required
def dashboard(request):
    user = request.user
    profile = user.userprofile
    
    # Get active quests
    active_quests = Quest.objects.filter(
        user=user,
        status='IN_PROGRESS'
    ).order_by('deadline')
    
    # Get daily progress
    daily_completed = UserQuest.objects.filter(
        user=user,
        completed=True,
        completed_at__date=timezone.now().date()
    ).count()
    
    daily_total = profile.daily_quest_limit
    daily_progress = (daily_completed / daily_total * 100) if daily_total > 0 else 0
    
    # Calculate XP progress
    required_xp = profile.level * 100
    xp_progress = (profile.experience / required_xp * 100) if required_xp > 0 else 0
    
    return render(request, 'core/dashboard.html', {
        'profile': profile,
        'active_quests': active_quests,
        'daily_completed': daily_completed,
        'daily_total': daily_total,
        'daily_progress': daily_progress,
        'xp_progress': xp_progress,
        'required_xp': required_xp
    })

@login_required
def quest_list(request):
    quests = Quest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/quest_list.html', {'quests': quests})

@login_required
def quest_create(request):
    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.user = request.user
            quest.calculate_rewards()
            quest.save()
            messages.success(request, 'New quest created!')
            return redirect('quest_list')
    else:
        ai_service = AIService()
        suggestions = ai_service.generate_quest_suggestions(request.user.userprofile)
        form = QuestForm()
    
    return render(request, 'core/quest_form.html', {
        'form': form,
        'quest_suggestions': suggestions
    })

@login_required
def quest_complete(request, quest_id):
    quest = get_object_or_404(Quest, id=quest_id, user=request.user)
    
    if quest.status != 'COMPLETED':
        quest.status = 'COMPLETED'
        quest.save()
        
        # Award XP and coins
        profile = request.user.userprofile
        profile.experience += quest.xp_reward
        profile.coins += quest.coin_reward
        
        # Check for level up
        if profile.level_up():
            messages.success(request, f'Level Up! You are now level {profile.level}!')
            profile.update_rank()
        
        profile.save()
        
        # Create achievement if applicable
        check_quest_achievements(request.user)
        
        messages.success(request, f'Quest completed! Earned {quest.xp_reward} XP and {quest.coin_reward} coins!')
    
    return redirect('quest_list')

@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user).order_by('deadline')
    return render(request, 'core/goal_list.html', {'goals': goals})

@login_required
def goal_create(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            
            # Generate quests for this goal
            ai_service = AIService()
            quests = ai_service.generate_quests_from_goal(request.user.userprofile, goal)
            
            # Create the quests
            for quest_data in quests:
                Quest.objects.create(
                    user=request.user,
                    title=quest_data['title'],
                    description=quest_data['description'],
                    difficulty=quest_data['difficulty'],
                    reward_xp=quest_data['reward_xp'],
                    reward_coins=quest_data['reward_coins'],
                    required_level=quest_data['required_level'],
                    deadline=quest_data.get('deadline', goal.deadline)
                )
            
            messages.success(request, 'Goal created! Check your quest list for auto-generated quests to help you achieve it.')
            return redirect('quest_list')
    else:
        form = GoalForm()
    
    return render(request, 'core/goal_form.html', {'form': form})

@login_required
def community_feed(request):
    posts = CommunityPost.objects.all().order_by('-created_at')
    return render(request, 'core/community.html', {'posts': posts})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            
            messages.success(request, 'Post created successfully!')
            return redirect('community_feed')
    else:
        form = CommunityPostForm()
    
    return render(request, 'core/post_form.html', {'form': form})

@login_required
def profile(request):
    user_profile = request.user.userprofile
    completed_quests = Quest.objects.filter(user=request.user, status='COMPLETED').count()
    active_quests = Quest.objects.filter(user=request.user, status='IN_PROGRESS').count()
    total_xp = user_profile.experience + (user_profile.level - 1) * 100
    
    context = {
        'user_profile': user_profile,
        'completed_quests': completed_quests,
        'active_quests': active_quests,
        'total_xp': total_xp,
    }
    return render(request, 'core/profile.html', context)

@login_required
def settings(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        profile_form = UserProfileSettingsForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, 'Your settings have been updated successfully!')
            return redirect('profile')
    else:
        form = UserSettingsForm(instance=request.user)
        profile_form = UserProfileSettingsForm(instance=request.user.userprofile)
    
    context = {
        'form': form,
        'profile_form': profile_form,
    }
    return render(request, 'core/settings.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileEditForm(instance=request.user.userprofile)
    
    context = {
        'form': form,
    }
    return render(request, 'core/profile_edit.html', context)

@login_required
def quest_start(request, quest_id):
    quest = get_object_or_404(Quest, id=quest_id, user=request.user)
    if quest.start_quest():
        messages.success(request, f'Quest "{quest.name}" has been started!')
    else:
        messages.error(request, 'Unable to start quest. Make sure it is available.')
    return redirect('quest_list')

@login_required
def quest_fail(request, quest_id):
    quest = get_object_or_404(Quest, id=quest_id, user=request.user)
    if quest.fail_quest():
        messages.warning(request, f'Quest "{quest.name}" has been marked as failed.')
    else:
        messages.error(request, 'Unable to fail quest. Make sure it is in progress.')
    return redirect('quest_list')

@login_required
def goal_edit(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully!')
            return redirect('goal_list')
    else:
        form = GoalForm(instance=goal)
    
    context = {
        'form': form,
        'goal': goal,
    }
    return render(request, 'core/goal_form.html', context)

@login_required
def goal_delete(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully!')
        return redirect('goal_list')
    
    context = {
        'goal': goal,
    }
    return render(request, 'core/goal_confirm_delete.html', context)

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'core/post_detail.html', context)

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, user=request.user)
    if request.method == 'POST':
        form = CommunityPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommunityPostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'core/post_form.html', context)

def about(request):
    return render(request, 'core/about.html')

def privacy(request):
    return render(request, 'core/privacy.html')

def terms(request):
    return render(request, 'core/terms.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data (send email, save to database, etc.)
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/contact.html', context)

# Helper Functions
def analyze_personality(answers):
    """
    Analyze quiz answers using a free personality analysis API
    Returns personality type and traits
    """
    # Example using a mock API (replace with actual free API)
    personality_types = {
        'achiever': {
            'strengths': ['goal-oriented', 'persistent', 'organized'],
            'weaknesses': ['perfectionist', 'workaholic']
        },
        'explorer': {
            'strengths': ['creative', 'adaptable', 'curious'],
            'weaknesses': ['unfocused', 'restless']
        },
        'socializer': {
            'strengths': ['empathetic', 'collaborative', 'communicative'],
            'weaknesses': ['dependent', 'conflict-avoidant']
        },
        'competitor': {
            'strengths': ['driven', 'ambitious', 'focused'],
            'weaknesses': ['impatient', 'overly competitive']
        }
    }
    
    # Simple scoring system (replace with API call)
    scores = {
        'achiever': 0,
        'explorer': 0,
        'socializer': 0,
        'competitor': 0
    }
    
    for answer in answers.values():
        if isinstance(answer, str):
            for ptype in scores:
                if ptype in answer.lower():
                    scores[ptype] += 1
    
    personality_type = max(scores, key=scores.get)
    traits = personality_types[personality_type]
    
    return {
        'type': personality_type,
        'strengths': traits['strengths'],
        'weaknesses': traits['weaknesses']
    }

def generate_goal_tasks(goal):
    """
    Generate tasks for a goal using AI recommendations
    """
    try:
        # Example task generation (replace with actual AI API call)
        default_tasks = [
            {
                'name': f'Plan {goal.title}',
                'description': 'Create a detailed plan with milestones',
                'difficulty': 'E',
                'duration_hours': 1
            },
            {
                'name': f'Research {goal.title}',
                'description': 'Gather necessary information and resources',
                'difficulty': 'D',
                'duration_hours': 2
            },
            {
                'name': f'Execute {goal.title} - Phase 1',
                'description': 'Begin implementation of the plan',
                'difficulty': 'C',
                'duration_hours': 4
            }
        ]
        
        for task in default_tasks:
            Quest.objects.create(
                user=goal.user,
                name=task['name'],
                description=task['description'],
                difficulty=task['difficulty'],
                duration_hours=task['duration_hours']
            )
            
    except Exception as e:
        print(f"Error generating tasks: {e}")

def check_quest_achievements(user):
    """
    Check and award achievements based on quest completion
    """
    completed_quests = UserQuest.objects.filter(
        user=user,
        completed=True
    ).count()
    
    # Achievement thresholds
    achievement_levels = {
        10: 'Novice Hunter',
        50: 'Expert Hunter',
        100: 'Master Hunter',
        500: 'Shadow Monarch'
    }
    
    for threshold, title in achievement_levels.items():
        if completed_quests >= threshold:
            Achievement.objects.get_or_create(
                user=user,
                name=title,
                defaults={
                    'description': f'Completed {threshold} quests',
                    'xp_reward': threshold * 10,
                    'coin_reward': threshold * 5
                }
            )