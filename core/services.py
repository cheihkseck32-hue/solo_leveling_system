from django.utils import timezone
from datetime import timedelta
import random

class AIService:
    """Service for AI-powered quest and goal generation"""
    
    def __init__(self):
        self.quest_templates = {
            'PRODUCTIVITY': [
                {
                    'title': 'Complete {task_count} {task_type}',
                    'description': 'Focus on completing {task_count} {task_type} to make progress on your goal.',
                    'difficulties': {
                        1: {'task_count': '2-3', 'xp': 100, 'coins': 10},
                        2: {'task_count': '4-5', 'xp': 200, 'coins': 20},
                        3: {'task_count': '6-8', 'xp': 300, 'coins': 30},
                    }
                },
                {
                    'title': 'Dedicate {time_amount} to {activity}',
                    'description': 'Spend focused time on {activity} without distractions.',
                    'difficulties': {
                        1: {'time_amount': '30 minutes', 'xp': 100, 'coins': 10},
                        2: {'time_amount': '1 hour', 'xp': 200, 'coins': 20},
                        3: {'time_amount': '2 hours', 'xp': 300, 'coins': 30},
                    }
                }
            ],
            'LEARNING': [
                {
                    'title': 'Study {topic} for {duration}',
                    'description': 'Focus on learning {topic} through active study and practice.',
                    'difficulties': {
                        1: {'duration': '30 minutes', 'xp': 100, 'coins': 10},
                        2: {'duration': '1 hour', 'xp': 200, 'coins': 20},
                        3: {'duration': '2 hours', 'xp': 400, 'coins': 40},
                    }
                },
                {
                    'title': 'Complete {count} exercises in {subject}',
                    'description': 'Practice and reinforce your knowledge by completing exercises.',
                    'difficulties': {
                        1: {'count': '3-5', 'xp': 150, 'coins': 15},
                        2: {'count': '6-8', 'xp': 300, 'coins': 30},
                        3: {'count': '9-12', 'xp': 450, 'coins': 45},
                    }
                }
            ],
            'FITNESS': [
                {
                    'title': '{exercise_type} Workout Session',
                    'description': 'Complete a {intensity} {exercise_type} workout session.',
                    'difficulties': {
                        1: {'intensity': 'light', 'xp': 100, 'coins': 10},
                        2: {'intensity': 'moderate', 'xp': 200, 'coins': 20},
                        3: {'intensity': 'intense', 'xp': 300, 'coins': 30},
                    }
                },
                {
                    'title': 'Achieve {target} {metric}',
                    'description': 'Push yourself to reach your fitness milestone.',
                    'difficulties': {
                        1: {'target': 'beginner', 'xp': 100, 'coins': 10},
                        2: {'target': 'intermediate', 'xp': 200, 'coins': 20},
                        3: {'target': 'advanced', 'xp': 300, 'coins': 30},
                    }
                }
            ]
        }
    
    def generate_quests_from_goal(self, user_profile, goal):
        """Generate a set of specific quests to help achieve the goal"""
        category = self._determine_goal_category(goal.title, goal.description)
        templates = self.quest_templates.get(category, self.quest_templates['PRODUCTIVITY'])
        
        quests = []
        num_quests = random.randint(3, 5)  # Generate 3-5 quests per goal
        
        for _ in range(num_quests):
            template = random.choice(templates)
            difficulty = random.randint(1, 3)  # Generate quests of varying difficulty
            
            quest_data = self._generate_quest_from_template(
                template, 
                difficulty,
                goal.title,
                goal.description
            )
            
            # Add deadline based on goal deadline if exists
            if goal.deadline:
                days_until_deadline = (goal.deadline - timezone.now()).days
                if days_until_deadline > 0:
                    quest_data['deadline'] = timezone.now() + timedelta(
                        days=random.randint(1, max(days_until_deadline, 1))
                    )
            
            quests.append(quest_data)
        
        return quests
    
    def _determine_goal_category(self, title, description):
        """Determine the most appropriate category for the goal"""
        title_desc = (title + " " + description).upper()
        
        if any(word in title_desc for word in ['STUDY', 'LEARN', 'COURSE', 'EDUCATION']):
            return 'LEARNING'
        elif any(word in title_desc for word in ['EXERCISE', 'WORKOUT', 'FITNESS', 'GYM']):
            return 'FITNESS'
        else:
            return 'PRODUCTIVITY'
    
    def _generate_quest_from_template(self, template, difficulty, goal_title, goal_description):
        """Generate a specific quest from a template"""
        difficulty_data = template['difficulties'][difficulty]
        
        # Extract key terms from goal
        keywords = self._extract_keywords(goal_title, goal_description)
        
        # Generate quest details
        quest_details = {
            'title': template['title'].format(**{
                **keywords,
                **difficulty_data,
                'task_type': keywords.get('activity', 'tasks'),
                'exercise_type': keywords.get('activity', 'fitness'),
                'topic': keywords.get('subject', 'the subject'),
                'subject': keywords.get('subject', 'the material'),
                'metric': keywords.get('metric', 'goal'),
            }),
            'description': template['description'].format(**{
                **keywords,
                **difficulty_data,
                'activity': keywords.get('activity', 'the task'),
                'topic': keywords.get('subject', 'the subject'),
            }),
            'difficulty': difficulty,
            'reward_xp': difficulty_data['xp'],
            'reward_coins': difficulty_data['coins'],
            'required_level': max(1, difficulty - 1),  # Higher difficulty quests require higher levels
        }
        
        return quest_details
    
    def _extract_keywords(self, title, description):
        """Extract relevant keywords from goal title and description"""
        text = (title + " " + description).lower()
        
        # Extract activity type
        activities = ['reading', 'writing', 'coding', 'studying', 'exercise', 
                     'meditation', 'practice', 'training', 'work']
        activity = next((word for word in activities if word in text), None)
        
        # Extract subject matter
        subjects = ['math', 'science', 'history', 'programming', 'language',
                   'project', 'presentation', 'report', 'analysis']
        subject = next((word for word in subjects if word in text), None)
        
        return {
            'activity': activity,
            'subject': subject,
        }
