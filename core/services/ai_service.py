from django.utils import timezone
from datetime import timedelta
import random

class AIService:
    """Service for AI-powered quest and goal generation"""
    
    def __init__(self):
        self.quest_templates = {
            'PRODUCTIVITY': [
                {
                    'title': 'Complete {task_count} tasks',
                    'description': 'Focus on completing {task_count} tasks to make progress on your goal.',
                    'difficulties': {
                        1: {'task_count': '2-3', 'xp': 100, 'coins': 10},
                        2: {'task_count': '4-5', 'xp': 200, 'coins': 20},
                        3: {'task_count': '6-8', 'xp': 300, 'coins': 30},
                        4: {'task_count': '9-12', 'xp': 500, 'coins': 50},
                        5: {'task_count': '15+', 'xp': 800, 'coins': 80}
                    },
                    'stat_focus': ['intelligence', 'sense']
                },
                {
                    'title': 'Work on {activity} for {time_amount}',
                    'description': 'Spend focused time on {activity} without distractions. {bonus_objective}',
                    'difficulties': {
                        1: {'time_amount': '30 minutes', 'bonus_objective': 'Take short breaks every 25 minutes.', 'xp': 100, 'coins': 10},
                        2: {'time_amount': '1 hour', 'bonus_objective': 'Document your progress.', 'xp': 200, 'coins': 20},
                        3: {'time_amount': '2 hours', 'bonus_objective': 'Share your learnings with others.', 'xp': 300, 'coins': 30},
                        4: {'time_amount': '4 hours', 'bonus_objective': 'Create a summary of your work.', 'xp': 500, 'coins': 50},
                        5: {'time_amount': '6 hours', 'bonus_objective': 'Teach someone what you learned.', 'xp': 800, 'coins': 80}
                    },
                    'stat_focus': ['intelligence', 'vitality']
                }
            ],
            'LEARNING': [
                {
                    'title': 'Master {subject}: {duration} Study Session',
                    'description': 'Focus on learning and practicing {subject}. {learning_strategy}',
                    'difficulties': {
                        1: {'duration': '30 minutes', 'learning_strategy': 'Take notes and review key concepts.', 'xp': 100, 'coins': 10},
                        2: {'duration': '1 hour', 'learning_strategy': 'Create mind maps or diagrams.', 'xp': 200, 'coins': 20},
                        3: {'duration': '2 hours', 'learning_strategy': 'Practice with real-world examples.', 'xp': 400, 'coins': 40},
                        4: {'duration': '3 hours', 'learning_strategy': 'Teach concepts to others.', 'xp': 600, 'coins': 60},
                        5: {'duration': '4 hours', 'learning_strategy': 'Create a comprehensive study guide.', 'xp': 1000, 'coins': 100}
                    },
                    'stat_focus': ['intelligence', 'sense']
                },
                {
                    'title': '{subject} Challenge: {count} Advanced Exercises',
                    'description': 'Push your limits with challenging {subject} exercises. {practice_goal}',
                    'difficulties': {
                        1: {'count': '3-5', 'practice_goal': 'Focus on fundamentals.', 'xp': 150, 'coins': 15},
                        2: {'count': '6-8', 'practice_goal': 'Tackle intermediate concepts.', 'xp': 300, 'coins': 30},
                        3: {'count': '9-12', 'practice_goal': 'Solve complex problems.', 'xp': 450, 'coins': 45},
                        4: {'count': '13-15', 'practice_goal': 'Create your own problems.', 'xp': 700, 'coins': 70},
                        5: {'count': '16-20', 'practice_goal': 'Master advanced techniques.', 'xp': 1000, 'coins': 100}
                    },
                    'stat_focus': ['intelligence', 'agility']
                }
            ],
            'FITNESS': [
                {
                    'title': '{intensity} Workout: {duration} Challenge',
                    'description': 'Complete a {intensity} workout session. {workout_focus}',
                    'difficulties': {
                        1: {'duration': '20 minutes', 'intensity': 'Light', 'workout_focus': 'Focus on proper form.', 'xp': 100, 'coins': 10},
                        2: {'duration': '40 minutes', 'intensity': 'Moderate', 'workout_focus': 'Increase repetitions.', 'xp': 200, 'coins': 20},
                        3: {'duration': '60 minutes', 'intensity': 'Intense', 'workout_focus': 'Add complex movements.', 'xp': 300, 'coins': 30},
                        4: {'duration': '90 minutes', 'intensity': 'Expert', 'workout_focus': 'Minimize rest periods.', 'xp': 500, 'coins': 50},
                        5: {'duration': '120 minutes', 'intensity': 'Elite', 'workout_focus': 'Achieve personal records.', 'xp': 800, 'coins': 80}
                    },
                    'stat_focus': ['strength', 'vitality']
                },
                {
                    'title': 'Endurance Challenge: {target}',
                    'description': 'Push your limits with this endurance challenge. {endurance_tip}',
                    'difficulties': {
                        1: {'target': '2000 steps', 'endurance_tip': 'Maintain a steady pace.', 'xp': 100, 'coins': 10},
                        2: {'target': '5000 steps', 'endurance_tip': 'Add intervals of speed.', 'xp': 200, 'coins': 20},
                        3: {'target': '10000 steps', 'endurance_tip': 'Include elevation changes.', 'xp': 300, 'coins': 30},
                        4: {'target': '15000 steps', 'endurance_tip': 'Track your heart rate.', 'xp': 500, 'coins': 50},
                        5: {'target': '20000 steps', 'endurance_tip': 'Maintain target heart rate.', 'xp': 800, 'coins': 80}
                    },
                    'stat_focus': ['vitality', 'agility']
                }
            ],
            'CREATIVITY': [
                {
                    'title': 'Creative Project: {project_scope}',
                    'description': 'Express yourself through creative work. {creative_prompt}',
                    'difficulties': {
                        1: {'project_scope': 'Quick Sketch', 'creative_prompt': 'Focus on basic techniques.', 'xp': 100, 'coins': 10},
                        2: {'project_scope': 'Detailed Drawing', 'creative_prompt': 'Experiment with new styles.', 'xp': 200, 'coins': 20},
                        3: {'project_scope': 'Mixed Media', 'creative_prompt': 'Combine multiple elements.', 'xp': 300, 'coins': 30},
                        4: {'project_scope': 'Portfolio Piece', 'creative_prompt': 'Tell a story through your work.', 'xp': 500, 'coins': 50},
                        5: {'project_scope': 'Masterwork', 'creative_prompt': 'Push artistic boundaries.', 'xp': 800, 'coins': 80}
                    },
                    'stat_focus': ['sense', 'intelligence']
                }
            ]
        }
    
    def generate_quest_suggestions(self, user_profile, goal=None):
        """Generate quest suggestions based on user profile and optional goal"""
        suggestions = []
        
        # Determine categories to generate suggestions from
        if goal:
            primary_category = self._determine_goal_category(goal.title, goal.description)
            categories = [primary_category]
            # Add related categories based on user stats
            if user_profile.strength > user_profile.intelligence:
                categories.append('FITNESS')
            if user_profile.intelligence > user_profile.strength:
                categories.append('LEARNING')
        else:
            # Select categories based on user stats and level
            categories = []
            if user_profile.strength >= 5:
                categories.append('FITNESS')
            if user_profile.intelligence >= 5:
                categories.append('LEARNING')
            if user_profile.sense >= 5:
                categories.append('CREATIVITY')
            if not categories:  # Fallback if no stats are high enough
                categories = list(self.quest_templates.keys())
        
        # Generate suggestions with dynamic difficulty
        for category in categories:
            templates = self.quest_templates.get(category, [])
            num_suggestions = min(len(templates), random.randint(2, 3))
            
            for _ in range(num_suggestions):
                template = random.choice(templates)
                
                # Calculate appropriate difficulty based on user stats
                max_difficulty = min(5, user_profile.level)
                if template.get('stat_focus'):
                    stat_levels = [getattr(user_profile, stat, 1) for stat in template['stat_focus']]
                    avg_stat_level = sum(stat_levels) / len(stat_levels)
                    max_difficulty = min(max_difficulty, int(avg_stat_level * 1.5))
                
                difficulty = random.randint(max(1, max_difficulty - 2), max_difficulty)
                
                quest_data = self._generate_quest_from_template(
                    template,
                    difficulty,
                    goal.title if goal else "",
                    goal.description if goal else "",
                    user_profile
                )
                
                # Add category and stat focus
                quest_data['category'] = category
                quest_data['stat_focus'] = template.get('stat_focus', [])
                suggestions.append(quest_data)
        
        return suggestions

    def generate_quests_from_goal(self, user_profile, goal):
        """Generate a set of specific quests to help achieve the goal"""
        category = self._determine_goal_category(goal.title, goal.description)
        templates = self.quest_templates.get(category, self.quest_templates['PRODUCTIVITY'])
        
        quests = []
        num_quests = random.randint(3, 5)  # Generate 3-5 quests per goal
        
        for _ in range(num_quests):
            template = random.choice(templates)
            difficulty = random.randint(1, min(3, user_profile.level))  # Cap difficulty by user level
            
            quest_data = self._generate_quest_from_template(
                template, 
                difficulty,
                goal.title,
                goal.description,
                user_profile
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
        elif any(word in title_desc for word in ['ART', 'CREATIVE', 'PROJECT', 'DESIGN']):
            return 'CREATIVITY'
        else:
            return 'PRODUCTIVITY'
    
    def _generate_quest_from_template(self, template, difficulty, goal_title, goal_description, user_profile):
        """Generate a specific quest from a template with personalization"""
        difficulty_data = template['difficulties'][difficulty]
        
        # Extract key terms from goal
        keywords = self._extract_keywords(goal_title, goal_description)
        
        # Create format dictionary with all possible variables
        format_dict = {
            # Template-specific variables
            **difficulty_data,
            
            # Extracted keywords
            'activity': keywords.get('activity', 'the task'),
            'subject': keywords.get('subject', 'your subject'),
            'topic': keywords.get('subject', 'the material'),
        }
        
        # Generate quest details
        quest_details = {
            'title': template['title'].format(**format_dict),
            'description': template['description'].format(**format_dict),
            'difficulty': difficulty,
            'reward_xp': self._calculate_personalized_xp(difficulty_data['xp'], user_profile),
            'reward_coins': self._calculate_personalized_coins(difficulty_data['coins'], user_profile),
            'required_level': max(1, difficulty - 1),
        }
        
        return quest_details
    
    def _calculate_personalized_xp(self, base_xp, user_profile):
        """Calculate personalized XP reward based on user stats and level"""
        # Apply level scaling
        level_bonus = 1 + (user_profile.level * 0.1)  # 10% increase per level
        
        # Apply stat scaling for relevant stats
        stat_bonus = 1
        if hasattr(user_profile, 'intelligence'):
            stat_bonus += (user_profile.intelligence * 0.05)  # 5% increase per intelligence point
        
        return int(base_xp * level_bonus * stat_bonus)
    
    def _calculate_personalized_coins(self, base_coins, user_profile):
        """Calculate personalized coin reward based on user stats and level"""
        # Apply level scaling
        level_bonus = 1 + (user_profile.level * 0.05)  # 5% increase per level
        
        # Apply stat scaling
        stat_bonus = 1
        if hasattr(user_profile, 'sense'):
            stat_bonus += (user_profile.sense * 0.03)  # 3% increase per sense point
        
        return int(base_coins * level_bonus * stat_bonus)
    
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
