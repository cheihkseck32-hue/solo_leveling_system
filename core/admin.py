from django.contrib import admin
from .models import (
    UserProfile, Goal, Quest, Achievement, CommunityPost,
    Comment, UserQuest, Penalty, Demand, Benefit, Mode,
    ShopItem, Exchange
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'rank', 'level', 'experience', 'coins')
    list_filter = ('rank', 'personality_type')
    search_fields = ('user__username', 'name')

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'goal_type', 'deadline', 'completion_percentage', 'total_quests_count')
    list_filter = ('goal_type', 'deadline', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'goal', 'difficulty', 'status', 'deadline')
    list_filter = ('status', 'difficulty', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'goal')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'achievement_type', 'xp_reward', 'unlocked_at')
    list_filter = ('achievement_type',)
    search_fields = ('name', 'user__username')

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'post_type', 'created_at')
    list_filter = ('post_type',)
    search_fields = ('title', 'user__username')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')

@admin.register(UserQuest)
class UserQuestAdmin(admin.ModelAdmin):
    list_display = ('user', 'quest', 'completed', 'started_at', 'completed_at')
    list_filter = ('completed',)
    search_fields = ('user__username', 'quest__title')

@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'xp_penalty', 'coin_penalty')
    search_fields = ('name', 'user__username')

@admin.register(Demand)
class DemandAdmin(admin.ModelAdmin):
    list_display = ('user', 'tasks', 'monthly', 'quests', 'skippers')
    search_fields = ('user__username',)

@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily', 'skip')
    search_fields = ('user__username',)

@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_required', 'coin_cost', 'duration_hours')
    search_fields = ('name',)

@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'points_required', 'ad_required')
    list_filter = ('product_type', 'ad_required')
    search_fields = ('name',)

@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('item', 'coin_value', 'point_value')
    search_fields = ('item',)
