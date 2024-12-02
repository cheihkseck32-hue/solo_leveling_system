from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, Quest, Goal, CommunityPost, Comment

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            placeholder = field.label if field.label else field_name.replace('_', ' ').title()
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter your {placeholder.lower()}'
            })

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar', 'personality_type')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'personality_type': forms.Select(choices=UserProfile.PERSONALITY_CHOICES)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ != 'Select':
                placeholder = field.label if field.label else field_name.replace('_', ' ').title()
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter your {placeholder.lower()}'
                })

class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ['title', 'description', 'difficulty', 'deadline', 'goal']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'difficulty': forms.Select(choices=Quest.DIFFICULTY_CHOICES)
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

        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ not in ['Select', 'DateTimeInput']:
                placeholder = field.label if field.label else field_name.replace('_', ' ').title()
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter {placeholder.lower()}'
                })

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__.__name__ != 'Select':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter your {field.label.lower()}'
                })

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter your {field.label.lower()}'
            })

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__.__name__ != 'Textarea' and field.widget.__class__.__name__ != 'TextInput':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter your {field.label.lower()}'
                })

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__.__name__ != 'Textarea':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter your {field.label.lower()}'
                })

class ProfileEditForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100
    )
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False
    )
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )
    # Make stats read-only
    strength = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    agility = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    vitality = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    sense = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    intelligence = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    notification_preferences = forms.JSONField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['name', 'title', 'bio', 'avatar', 'strength', 'agility', 
                 'vitality', 'sense', 'intelligence', 'notification_preferences']

    def clean(self):
        cleaned_data = super().clean()
        # Add any custom validation here if needed
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment...'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter your {field.label.lower()}'
            })

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__.__name__ != 'Textarea':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter your {field.label.lower()}'
                })
