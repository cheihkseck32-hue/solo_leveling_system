from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, Quest, Goal, CommunityPost, Comment

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('name', 'personality_type')
        widgets = {
            'personality_type': forms.Select(choices=UserProfile.PERSONALITY_CHOICES)
        }

class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ['title', 'description', 'difficulty', 'deadline', 'goal']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'difficulty': forms.Select(choices=Quest.DIFFICULTY_CHOICES),
            'goal': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['goal'].queryset = Goal.objects.filter(user=user, is_active=True)
            self.fields['goal'].empty_label = "No specific goal"
        
        self.fields['difficulty'].help_text = "Higher difficulty = higher rewards"
        self.fields['deadline'].required = False
        self.fields['goal'].required = False

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'description', 'goal_type', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your goal title...',
                'data-aos': 'fade-right'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your goal in detail...\n\nTip: Include specific outcomes and why this goal matters to you.',
                'rows': 4,
                'data-aos': 'fade-right',
                'data-aos-delay': '100'
            }),
            'goal_type': forms.Select(attrs={
                'class': 'form-control',
                'data-aos': 'fade-right',
                'data-aos-delay': '200'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'data-aos': 'fade-right',
                'data-aos-delay': '300'
            })
        }
        labels = {
            'title': 'Goal Title',
            'description': 'Description',
            'goal_type': 'Goal Type',
            'deadline': 'Target Completion Date'
        }
        help_texts = {
            'title': 'What do you want to achieve? Be specific and inspiring.',
            'description': 'Break down your goal. What does success look like?',
            'goal_type': 'Choose the type of goal to help our AI create better quests.',
            'deadline': 'When do you want to achieve this goal?'
        }

    def clean(self):
        cleaned_data = super().clean()
        deadline = cleaned_data.get('deadline')
        
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("The deadline cannot be in the past.")
        
        return cleaned_data

class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ('title', 'content', 'post_type')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            'post_type': forms.Select(choices=CommunityPost.POST_TYPES)
        }

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UserProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['title', 'bio', 'avatar', 'notification_preferences']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'notification_preferences': forms.TextInput(attrs={
                'class': 'json-editor',
                'data-type': 'json'
            })
        }

    def clean_notification_preferences(self):
        data = self.cleaned_data['notification_preferences']
        if isinstance(data, str):
            try:
                import json
                return json.loads(data)
            except json.JSONDecodeError:
                return {}
        return data

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['title', 'bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment...'})
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
