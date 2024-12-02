from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('personality-quiz/', views.personality_quiz, name='personality_quiz'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('profile/settings/', views.settings, name='settings'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/settings/', views.settings, name='settings'),
    
    # Quest URLs
    path('quests/', views.quest_list, name='quest_list'),
    path('quests/create/', views.quest_create, name='quest_create'),
    path('quests/<int:quest_id>/complete/', views.quest_complete, name='quest_complete'),
    path('quests/<int:quest_id>/start/', views.quest_start, name='quest_start'),
    path('quests/<int:quest_id>/fail/', views.quest_fail, name='quest_fail'),
    
    # Goal URLs
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:goal_id>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:goal_id>/delete/', views.goal_delete, name='goal_delete'),
    
    # Community URLs
    path('community/', views.community_feed, name='community_feed'),
    path('community/post/create/', views.post_create, name='post_create'),
    path('community/post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('community/post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    
    # Store URLs
    path('store/', views.store, name='store'),
    path('purchase/<int:item_id>/', views.purchase_item, name='purchase_item'),
    
    # Static Pages
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('contact/', views.contact, name='contact'),
]
