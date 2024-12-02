from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

def validate_rank(value):
    valid_ranks = ['E', 'D', 'C', 'B', 'A', 'S']
    if value not in valid_ranks:
        raise ValidationError(f'{value} is not a valid rank. Must be one of {valid_ranks}')

class UserProfile(models.Model):
    RANK_CHOICES = [
        ('E', 'E-Rank'),
        ('D', 'D-Rank'),
        ('C', 'C-Rank'),
        ('B', 'B-Rank'),
        ('A', 'A-Rank'),
        ('S', 'S-Rank'),
    ]
    
    PERSONALITY_CHOICES = [
        ('achiever', 'Achiever'),
        ('explorer', 'Explorer'),
        ('socializer', 'Socializer'),
        ('competitor', 'Competitor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Hunter')
    rank = models.CharField(max_length=1, choices=RANK_CHOICES, default='E', validators=[validate_rank])
    level = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    experience = models.PositiveIntegerField(default=0)
    coins = models.PositiveIntegerField(default=0)
    personality_type = models.CharField(max_length=20, choices=PERSONALITY_CHOICES, default='achiever')
    title = models.CharField(max_length=100, default='Novice Hunter')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    notification_preferences = models.JSONField(default=dict)
    strengths = models.JSONField(default=dict)
    weaknesses = models.JSONField(default=dict)
    daily_quest_limit = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    last_quest_completion = models.DateTimeField(null=True, blank=True)
    quest_streak = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['rank']),
            models.Index(fields=['level']),
            models.Index(fields=['personality_type']),
        ]
    
    def level_up(self):
        required_exp = self.level * 100
        if self.experience >= required_exp:
            self.level += 1
            self.experience -= required_exp
            self.daily_quest_limit = min(self.daily_quest_limit + 1, 10)
            self.update_rank()
            return True
        return False
    
    def add_experience(self, amount):
        self.experience += amount
        while self.level_up():
            pass
        self.save()
    
    def update_quest_streak(self):
        now = timezone.now()
        if self.last_quest_completion:
            days_since_last = (now - self.last_quest_completion).days
            if days_since_last <= 1:
                self.quest_streak += 1
            else:
                self.quest_streak = 0
        self.last_quest_completion = now
        self.save()

    def update_rank(self):
        if self.level >= 50:
            self.rank = 'S'
        elif self.level >= 40:
            self.rank = 'A'
        elif self.level >= 30:
            self.rank = 'B'
        elif self.level >= 20:
            self.rank = 'C'
        elif self.level >= 10:
            self.rank = 'D'
        else:
            self.rank = 'E'
        self.save()
    
    def can_take_quest(self, quest):
        return (
            self.level >= quest.required_level and
            self.daily_quests_taken() < self.daily_quest_limit
        )
    
    def daily_quests_taken(self):
        today = timezone.now().date()
        return UserQuest.objects.filter(
            user=self.user,
            started_at__date=today
        ).count()

    def __str__(self):
        return f"{self.name} (Rank {self.rank})"

class Goal(models.Model):
    GOAL_TYPES = [
        ('SHORT', 'Short Term'),
        ('LONG', 'Long Term'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=10, choices=GOAL_TYPES, default='SHORT')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    xp_reward = models.PositiveIntegerField(default=100)
    required_level = models.PositiveIntegerField(default=1)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'completed']),
            models.Index(fields=['deadline']),
        ]
    
    def is_overdue(self):
        return not self.completed and timezone.now() > self.deadline
    
    def complete(self):
        if not self.completed:
            self.completed = True
            self.progress = 100.0
            self.save()
            
            profile = self.user.userprofile
            profile.add_experience(self.xp_reward)
    
    def update_progress(self, new_progress):
        self.progress = min(max(new_progress, 0.0), 100.0)
        if self.progress >= 100.0:
            self.complete()
        self.save()

    def __str__(self):
        return self.title

class Quest(models.Model):
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='EASY')
    reward_xp = models.PositiveIntegerField(default=50)
    reward_coins = models.PositiveIntegerField(default=25)
    required_level = models.PositiveIntegerField(default=1)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['difficulty']),
            models.Index(fields=['required_level']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def calculate_rewards(self):
        """Calculate rewards based on difficulty and required level"""
        difficulty_multipliers = {
            'EASY': 1,
            'MEDIUM': 2,
            'HARD': 3,
        }
        multiplier = difficulty_multipliers.get(self.difficulty, 1)
        self.reward_xp = 50 * multiplier * self.required_level
        self.reward_coins = 25 * multiplier * self.required_level
    
    def is_available(self):
        return self.status == 'AVAILABLE'
    
    def is_completed(self):
        return self.status == 'COMPLETED'
    
    def is_in_progress(self):
        return self.status == 'IN_PROGRESS'
    
    def is_failed(self):
        return self.status == 'FAILED'
    
    def start_quest(self):
        if self.is_available():
            self.status = 'IN_PROGRESS'
            self.save()
    
    def complete_quest(self):
        if self.is_in_progress():
            self.status = 'COMPLETED'
            self.save()
            # Award rewards to user
            profile = self.user.userprofile
            profile.experience += self.reward_xp
            profile.coins += self.reward_coins
            profile.save()
    
    def fail_quest(self):
        if self.is_in_progress():
            self.status = 'FAILED'
            self.save()
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('MILESTONE', 'Milestone'),
        ('SKILL', 'Skill Mastery'),
        ('STREAK', 'Streak'),
        ('SPECIAL', 'Special'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES, default='MILESTONE')
    xp_reward = models.PositiveIntegerField(default=0)
    coin_reward = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    icon = models.CharField(max_length=50, default='trophy')
    unlocked_at = models.DateTimeField(null=True, blank=True)
    progress = models.FloatField(default=0.0)
    required_value = models.PositiveIntegerField(default=1)
    
    class Meta:
        indexes = [
            models.Index(fields=['achievement_type']),
            models.Index(fields=['required_value']),
        ]
    
    def is_unlocked(self):
        return self.progress >= self.required_value
    
    def update_progress(self, new_progress):
        self.progress = min(max(new_progress, 0.0), 100.0)
        if self.is_unlocked():
            self.unlocked_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name

class CommunityPost(models.Model):
    POST_TYPES = [
        ('ACHIEVEMENT', 'Achievement'),
        ('QUESTION', 'Question'),
        ('DISCUSSION', 'Discussion'),
        ('GUIDE', 'Guide'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='DISCUSSION')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['post_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

class UserQuest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['quest']),
        ]
    
    def __str__(self):
        return f"{self.quest.name} by {self.user.username}"

class Penalty(models.Model):
    name = models.CharField(max_length=100)
    xp_penalty = models.PositiveIntegerField(default=0)
    coin_penalty = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['xp_penalty']),
        ]
    
    def __str__(self):
        return self.name

class Demand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tasks = models.PositiveIntegerField(default=0)
    monthly = models.PositiveIntegerField(default=0)
    quests = models.PositiveIntegerField(default=0)
    skippers = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['tasks']),
        ]
    
    def __str__(self):
        return f"Demand for {self.user.username}"

class Benefit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    daily = models.PositiveIntegerField(default=0)
    skip = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['daily']),
        ]
    
    def __str__(self):
        return f"Benefit for {self.user.username}"

class Mode(models.Model):
    name = models.CharField(max_length=100)
    level_required = models.PositiveIntegerField(default=0)
    coin_cost = models.PositiveIntegerField(default=0)
    duration_hours = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['level_required']),
            models.Index(fields=['coin_cost']),
        ]
    
    def __str__(self):
        return self.name

class ShopItem(models.Model):
    DIGITAL_PRODUCT_TYPES = [
        ('BOOK', 'Book'),
        ('AUDIO', 'Audio'),
        ('STICKER', 'Sticker'),
    ]

    name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=10, choices=DIGITAL_PRODUCT_TYPES, default='BOOK')
    digital_file = models.FileField(upload_to='digital_products/', blank=True, null=True)
    points_required = models.PositiveIntegerField()
    ad_required = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['product_type']),
            models.Index(fields=['points_required']),
        ]
    
    def __str__(self):
        return self.name

class Exchange(models.Model):
    item = models.CharField(max_length=100)
    coin_value = models.PositiveIntegerField(default=0)
    point_value = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['coin_value']),
        ]
    
    def __str__(self):
        return self.item
