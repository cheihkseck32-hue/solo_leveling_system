from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Yuki')
    level = models.PositiveIntegerField(default=0)
    experience = models.PositiveIntegerField(default=0)
    coins = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Quest(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    xp_reward = models.PositiveIntegerField(default=0)
    coin_reward = models.PositiveIntegerField(default=0)
    duration_hours = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class UserQuest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class Penalty(models.Model):
    name = models.CharField(max_length=100)
    xp_penalty = models.PositiveIntegerField(default=0)
    coin_penalty = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Demand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tasks = models.PositiveIntegerField(default=0)
    monthly = models.PositiveIntegerField(default=0)
    quests = models.PositiveIntegerField(default=0)
    skippers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Demand for {self.user.username}"





class Benefit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    daily = models.PositiveIntegerField(default=0)
    skip = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Benefit for {self.user.username}"



class Mode(models.Model):
    name = models.CharField(max_length=100)
    level_required = models.PositiveIntegerField(default=0)
    coin_cost = models.PositiveIntegerField(default=0)
    duration_hours = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name



class ShopItem(models.Model):
    DIGITAL_PRODUCT_TYPES = [
        ('BOOK', 'Book'),
        ('AUDIO', 'Audio'),
        ('STICKER', 'Sticker'),
    ]

    name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=10, choices=DIGITAL_PRODUCT_TYPES)
    digital_file = models.FileField(upload_to='digital_products/', blank=True, null=True)
    points_required = models.PositiveIntegerField()
    ad_required = models.BooleanField(default=False)  # If True, user can get the item by watching an ad
    
    def __str__(self):
        return self.name


class Exchange(models.Model):
    item = models.CharField(max_length=100)
    coin_value = models.PositiveIntegerField(default=0)
    point_value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.item


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    xp_reward = models.PositiveIntegerField(default=0)
    coin_reward = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
