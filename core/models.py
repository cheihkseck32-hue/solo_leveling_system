from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import random

def validate_rank(value):
    valid_ranks = ['F', 'E', 'D', 'C', 'B', 'A', 'S']
    if value not in valid_ranks:
        raise ValidationError(f'{value} is not a valid rank. Must be one of {valid_ranks}')

class UserProfile(models.Model):
    RANK_CHOICES = [
        ('F', 'F-Rank Hunter'),
        ('E', 'E-Rank Hunter'),
        ('D', 'D-Rank Hunter'),
        ('C', 'C-Rank Hunter'),
        ('B', 'B-Rank Hunter'),
        ('A', 'A-Rank Hunter'),
        ('S', 'S-Rank Hunter'),
    ]
    
    PERSONALITY_CHOICES = [
        ('achiever', 'Achiever'),
        ('explorer', 'Explorer'),
        ('socializer', 'Socializer'),
        ('competitor', 'Competitor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Hunter')
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    rank = models.CharField(max_length=1, choices=RANK_CHOICES, default='F', validators=[validate_rank])
    personality_type = models.CharField(max_length=50, blank=True, null=True)
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
    inventory = models.JSONField(default=list, blank=True)
    strength = models.IntegerField(default=10)
    agility = models.IntegerField(default=10)
    vitality = models.IntegerField(default=10)
    sense = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    
    class Meta:
        indexes = [
            models.Index(fields=['rank']),
            models.Index(fields=['level']),
            models.Index(fields=['personality_type']),
        ]
    
    @property
    def level_progress(self):
        """Calculate the progress percentage to the next level"""
        xp_for_next_level = self.xp_to_next_level()
        xp_from_last_level = self.level * 100  # Base XP needed for current level
        current_level_xp = self.experience - xp_from_last_level
        return min(100, int((current_level_xp / xp_for_next_level) * 100))

    def xp_to_next_level(self):
        """Calculate XP needed for next level"""
        return (self.level + 1) * 100

    def get_next_rank(self):
        """Get the next rank based on current rank"""
        current_rank_index = [choice[0] for choice in self.RANK_CHOICES].index(self.rank)
        if current_rank_index < len(self.RANK_CHOICES) - 1:
            return self.RANK_CHOICES[current_rank_index + 1][1]
        return self.RANK_CHOICES[-1][1]  # Return highest rank if already at max

    def add_experience(self, amount):
        """Add experience points and handle level ups"""
        self.experience += amount
        while self.experience >= self.xp_to_next_level():
            self.level_up()

    def level_up(self):
        """Handle level up logic"""
        self.level += 1
        # Update rank based on level
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
        elif self.level >= 5:
            self.rank = 'E'
        self.daily_quest_limit = min(self.daily_quest_limit + 1, 10)
        self.save()

    def gain_experience(self, amount):
        self.experience += amount
        while self.experience >= self.xp_to_next_level():
            self.level_up()
        self.save()

    def complete_quest(self, quest):
        if quest.status == 'completed':
            self.gain_experience(quest.reward_xp)
            self.coins += quest.reward_coins
            quest.completed_at = timezone.now()
            quest.save()
        else:
            raise ValueError("Quest is not completed yet.")

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

    def add_item_to_inventory(self, item):
        self.inventory.append(item)
        self.save()

    def update_stats_from_quest(self, quest_type):
        if quest_type == 'study':
            self.intelligence += 1
        elif quest_type == 'sport':
            self.strength += 1
        # Add more quest types and corresponding stat increases here
        self.save()

    def apply_item_effects(self, item):
        # Example: item.effects = {'strength': 3, 'intelligence': 2}
        for stat, increase in item.effects.items():
            if hasattr(self, stat):
                setattr(self, stat, getattr(self, stat) + increase)
        self.save()

    def get_total_stats(self):
        """Calculate total stats including item effects."""
        total_stats = {
            'strength': self.strength,
            'agility': self.agility,
            'vitality': self.vitality,
            'sense': self.sense,
            'intelligence': self.intelligence,
        }
        
        # Add effects from equipped items
        for item in self.inventory:
            for effect, value in item.get('effects', {}).items():
                if effect in total_stats:
                    total_stats[effect] += value
        
        return total_stats

    def get_equipped_items(self):
        """Retrieve equipped items from inventory."""
        return [item for item in self.inventory if item.get('equipped', False)]

    def __str__(self):
        return f"{self.name} (Rank {self.rank})"

class Goal(models.Model):
    GOAL_TYPES = [
        ('personal', 'Personal Development'),
        ('career', 'Career'),
        ('health', 'Health & Fitness'),
        ('education', 'Education'),
        ('financial', 'Financial'),
        ('creative', 'Creative'),
        ('social', 'Social'),
        ('other', 'Other')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default='personal')
    deadline = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return self.title

    @property
    def completion_percentage(self):
        total_quests = self.quests.count()
        if total_quests == 0:
            return 0
        completed_quests = self.quests.filter(status='completed').count()
        return int((completed_quests / total_quests) * 100)

    @property
    def completed_quests_count(self):
        return self.quests.filter(status='completed').count()

    @property
    def active_quests_count(self):
        return self.quests.filter(status='in_progress').count()

    @property
    def total_quests_count(self):
        return self.quests.count()

    @property
    def is_completed(self):
        return self.completion_percentage == 100

    class Meta:
        indexes = [
            models.Index(fields=['user', 'deadline']),
            models.Index(fields=['user', 'is_active']),
        ]
        ordering = ['-created_at']

class Quest(models.Model):
    QUEST_STATUS = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    DIFFICULTY_CHOICES = [
        (1, 'EASY'),
        (2, 'MEDIUM'),
        (3, 'HARD'),
        (4, 'EXPERT'),
        (5, 'LEGENDARY')
    ]

    QUEST_TYPES = [
        ('strength', 'Strength'),
        ('agility', 'Agility'),
        ('vitality', 'Vitality'),
        ('sense', 'Sense'),
        ('intelligence', 'Intelligence'),
        ('general', 'General')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    quest_type = models.CharField(
        max_length=20,
        choices=QUEST_TYPES,
        default='general'
    )
    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=1,
        help_text="Quest difficulty level"
    )
    reward_xp = models.IntegerField(default=100)
    reward_coins = models.IntegerField(default=10)
    required_level = models.IntegerField(default=1)
    deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=QUEST_STATUS, default='not_started')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey('Goal', on_delete=models.CASCADE, related_name='quests', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def calculate_xp_reward(self):
        """Calculate XP reward based on difficulty and other factors"""
        base_xp = self.reward_xp
        multiplier = {
            1: 1.0,    # EASY
            2: 1.5,    # MEDIUM
            3: 2.0,    # HARD
            4: 3.0,    # EXPERT
            5: 5.0     # LEGENDARY
        }.get(self.difficulty, 1.0)
        
        # Add time-based bonus (if completed before deadline)
        time_bonus = 1.0
        if self.deadline and self.completed_at:
            if self.completed_at < self.deadline:
                # Up to 50% bonus for early completion
                time_remaining = (self.deadline - self.completed_at).total_seconds()
                total_time = (self.deadline - self.created_at).total_seconds()
                time_bonus = 1.0 + (0.5 * (time_remaining / total_time))

        # Add streak bonus if user has an active streak
        streak_bonus = 1.0
        if hasattr(self.user, 'userprofile'):
            streak = self.user.userprofile.quest_streak
            if streak > 0:
                # Up to 30% bonus for streaks
                streak_bonus = 1.0 + min(streak * 0.1, 0.3)

        final_xp = int(base_xp * multiplier * time_bonus * streak_bonus)
        return max(final_xp, base_xp)  # Never give less than base XP

    def calculate_coin_reward(self):
        """Calculate coin reward based on difficulty and other factors"""
        base_coins = self.reward_coins
        multiplier = {
            1: 1.0,    # EASY
            2: 1.5,    # MEDIUM
            3: 2.0,    # HARD
            4: 3.0,    # EXPERT
            5: 5.0     # LEGENDARY
        }.get(self.difficulty, 1.0)
        
        # Add level bonus (higher level quests give more coins)
        level_bonus = 1.0 + (self.required_level - 1) * 0.05  # 5% more per level

        # Add random bonus chance (lucky drops)
        lucky_bonus = 1.0
        if random.random() < 0.1:  # 10% chance
            lucky_bonus = random.uniform(1.2, 2.0)  # 20-100% bonus

        final_coins = int(base_coins * multiplier * level_bonus * lucky_bonus)
        return max(final_coins, base_coins)  # Never give less than base coins

    def get_difficulty_color(self):
        colors = {
            1: 'success',   # Easy
            2: 'info',      # Medium
            3: 'warning',   # Hard
            4: 'danger',    # Expert
            5: 'dark'       # Legendary
        }
        return colors.get(self.difficulty, 'secondary')

    def get_status_color(self):
        colors = {
            'not_started': 'secondary',
            'in_progress': 'primary',
            'completed': 'success',
            'failed': 'danger'
        }
        return colors.get(self.status, 'secondary')

    def complete(self):
        """Complete the quest and award rewards"""
        if self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            
            # Calculate rewards
            xp_reward = self.calculate_xp_reward()
            coin_reward = self.calculate_coin_reward()
            
            # Award XP and coins to user
            profile = self.user.userprofile
            profile.add_experience(xp_reward)
            profile.coins += coin_reward

            # Update stats based on quest type and difficulty
            stat_increase = self.calculate_stat_increase()
            if self.quest_type != 'general':
                current_stat = getattr(profile, self.quest_type)
                setattr(profile, self.quest_type, current_stat + stat_increase)
            
            profile.save()
            self.save()
            
            return xp_reward, coin_reward
        return 0, 0

    def calculate_stat_increase(self):
        """Calculate stat increase based on difficulty"""
        base_increase = {
            1: 1,  # EASY
            2: 2,  # MEDIUM
            3: 3,  # HARD
            4: 4,  # EXPERT
            5: 5   # LEGENDARY
        }
        return base_increase.get(self.difficulty, 1)

    def fail(self):
        """Mark the quest as failed"""
        if self.status != 'failed':
            self.status = 'failed'
            self.save()

    def start(self):
        """Start the quest"""
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.save()

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_failed(self):
        return self.status == 'failed'

    @property
    def is_active(self):
        return self.status == 'in_progress'

    @property
    def difficulty_name(self):
        """Get the display name for the difficulty level"""
        return dict(self.DIFFICULTY_CHOICES).get(self.difficulty, 'Unknown')

    def completion_percentage(self):
        """Calculate the completion percentage for in-progress quests"""
        if self.status == 'completed':
            return 100
        elif self.status == 'not_started':
            return 0
        elif self.status == 'in_progress':
            if self.deadline:
                total_time = (self.deadline - self.created_at).total_seconds()
                elapsed_time = (timezone.now() - self.created_at).total_seconds()
                percentage = min(100, max(0, (elapsed_time / total_time) * 100))
                return round(percentage, 1)
            return 50  # Default to 50% if no deadline
        return 0

    def __str__(self):
        return f"{self.title} ({self.difficulty_name})"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['goal', 'status']),
            models.Index(fields=['completed_at']),
        ]
        ordering = ['-created_at']

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
    ITEM_TYPES = [
        ('CONSUMABLE', 'Consumable'),
        ('EQUIPMENT', 'Equipment'),
        ('WEAPON', 'Weapon'),
    ]
    
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    
    STAT_TYPES = [
        ('strength', 'Strength'),
        ('agility', 'Agility'),
        ('vitality', 'Vitality'),
        ('sense', 'Sense'),
        ('intelligence', 'Intelligence'),
    ]
    
    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='CONSUMABLE')
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    stat_type = models.CharField(max_length=20, choices=STAT_TYPES, null=True, blank=True)
    stat_increase = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, default='box')

    def purchase(self, user_profile):
        """Process item purchase and apply effects"""
        if user_profile.coins >= self.price:
            # Deduct coins
            user_profile.coins -= self.price
            
            # Add stat increase if applicable
            if self.stat_type and self.stat_increase > 0:
                current_stat = getattr(user_profile, self.stat_type)
                setattr(user_profile, self.stat_type, current_stat + self.stat_increase)
            
            # Add to inventory
            inventory = user_profile.inventory or []
            inventory.append({
                'id': self.id,
                'name': self.name,
                'type': self.item_type,
                'rarity': self.rarity,
                'stat_type': self.stat_type,
                'stat_increase': self.stat_increase,
                'icon': self.icon,
                'equipped': False,
                'purchased_at': timezone.now().isoformat()
            })
            user_profile.inventory = inventory
            
            # Save changes
            user_profile.save()
            return True
        return False

    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"

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
