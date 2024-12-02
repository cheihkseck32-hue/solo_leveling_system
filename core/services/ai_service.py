import openai
from django.conf import settings
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def generate_quests_from_goal(self, user_profile, goal, quest_count: int = 5) -> List[Dict]:
        """
        Generate a series of smaller quests that help achieve a larger goal
        """
        prompt = self._create_goal_based_quest_prompt(user_profile, goal)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a quest generator for a Solo Leveling inspired productivity system. 
                    Break down large goals into smaller, manageable quests that feel like a game progression.
                    Each quest should be specific, measurable, and achievable within 1-3 days.
                    Make the quests engaging and fun while maintaining focus on real progress."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            quest_text = response.choices[0].message.content
            return self._parse_quest_sequence(quest_text, user_profile.level)
            
        except Exception as e:
            # Fallback quest generation
            return self._generate_fallback_quests(goal, quest_count)

    def _create_goal_based_quest_prompt(self, user_profile, goal) -> str:
        """
        Create a detailed prompt for generating a sequence of quests based on a goal
        """
        base_prompt = f"""
        Generate a sequence of 5 engaging quests to help achieve this goal:
        
        GOAL: {goal.title}
        DESCRIPTION: {goal.description}
        DEADLINE: {goal.deadline.strftime('%Y-%m-%d')}
        
        User Profile:
        - Level: {user_profile.level}
        - Rank: {user_profile.rank}
        - Personality: {user_profile.personality_type}
        - Strengths: {', '.join(user_profile.strengths.keys()) if user_profile.strengths else 'Not specified'}
        - Weaknesses: {', '.join(user_profile.weaknesses.keys()) if user_profile.weaknesses else 'Not specified'}
        
        Requirements for each quest:
        1. Make it feel like a game quest while being practical
        2. Include specific, measurable objectives
        3. Should be completable in 1-3 days
        4. Match the user's personality type and preferences
        5. Gradually increase in difficulty
        6. Include clear rewards (XP and coins)
        7. Add gaming-style flavor text to make it engaging
        
        Format each quest as:
        QUEST_1:
        TITLE: [Engaging quest title]
        DESCRIPTION: [Detailed description with gaming flavor]
        OBJECTIVES: [Specific, measurable tasks]
        DIFFICULTY: [EASY/MEDIUM/HARD]
        XP_REWARD: [50-300]
        COIN_REWARD: [25-150]
        REQUIRED_LEVEL: [Appropriate level]
        ESTIMATED_DAYS: [1-3]
        
        [Repeat for QUEST_2 through QUEST_5, increasing in challenge]
        """
        return base_prompt

    def _parse_quest_sequence(self, response_text: str, user_level: int) -> List[Dict]:
        """
        Parse the AI response into a sequence of structured quests
        """
        quests = []
        current_quest = {}
        
        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('QUEST_'):
                if current_quest:
                    quests.append(current_quest)
                current_quest = {}
                continue
                
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'title':
                    current_quest['title'] = value
                elif key == 'description':
                    current_quest['description'] = value
                elif key == 'objectives':
                    current_quest['description'] = f"{current_quest.get('description', '')}\n\nObjectives:\n{value}"
                elif key == 'difficulty':
                    current_quest['difficulty'] = value.upper()
                elif key == 'xp_reward':
                    current_quest['reward_xp'] = int(value.split()[0])
                elif key == 'coin_reward':
                    current_quest['reward_coins'] = int(value.split()[0])
                elif key == 'required_level':
                    current_quest['required_level'] = min(int(value.split()[0]), max(1, user_level - 2))
                elif key == 'estimated_days':
                    days = int(value.split()[0])
                    current_quest['deadline'] = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        if current_quest:
            quests.append(current_quest)
            
        return quests

    def _generate_fallback_quests(self, goal, count: int) -> List[Dict]:
        """
        Generate fallback quests if the AI service fails
        """
        base_quests = [
            {
                'title': 'Plan Your Journey',
                'description': f'Create a detailed plan to achieve your goal: {goal.title}\n\nObjectives:\n1. Break down the goal into smaller steps\n2. Identify key milestones\n3. Set realistic deadlines',
                'difficulty': 'EASY',
                'reward_xp': 50,
                'reward_coins': 25,
                'required_level': 1,
                'deadline': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            {
                'title': 'Gather Resources',
                'description': f'Collect everything you need to progress towards: {goal.title}\n\nObjectives:\n1. List required resources\n2. Research best practices\n3. Organize your workspace',
                'difficulty': 'EASY',
                'reward_xp': 75,
                'reward_coins': 35,
                'required_level': 1,
                'deadline': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            },
            {
                'title': 'First Milestone',
                'description': f'Complete your first major step towards: {goal.title}\n\nObjectives:\n1. Focus on the first milestone\n2. Document your progress\n3. Reflect on learnings',
                'difficulty': 'MEDIUM',
                'reward_xp': 100,
                'reward_coins': 50,
                'required_level': 2,
                'deadline': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
            }
        ]
        return base_quests[:count]

    def generate_quest_suggestions(self, user_profile):
        """Generate quest suggestions based on user profile and preferences."""
        try:
            prompt = f"""Generate 3 quest suggestions for a user with the following profile:
            - Level: {user_profile.level}
            - Rank: {user_profile.rank}
            - Personality Type: {user_profile.personality_type}
            
            Format each quest as a dictionary with:
            - title: An engaging quest title
            - description: Detailed quest description
            - difficulty: A number from 1-5
            - xp_reward: XP points (100-500)
            - coin_reward: Coins (10-100)
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quest generator for a Solo Leveling inspired productivity system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Parse the response and extract quest suggestions
            suggestions_text = response.choices[0].message.content
            
            # Convert the text response to a list of quest dictionaries
            import ast
            suggestions = []
            
            # Split the response by lines and look for dictionary-like structures
            lines = suggestions_text.split('\n')
            current_dict = ""
            for line in lines:
                if line.strip():
                    current_dict += line
                    if line.strip().endswith('}'):
                        try:
                            quest_dict = ast.literal_eval(current_dict)
                            suggestions.append(quest_dict)
                            current_dict = ""
                        except:
                            current_dict = ""

            return suggestions[:3]  # Return at most 3 suggestions

        except Exception as e:
            print(f"Error generating quest suggestions: {str(e)}")
            # Return some default suggestions if AI generation fails
            return [
                {
                    'title': 'Complete Daily Tasks',
                    'description': 'Complete all your planned tasks for today.',
                    'difficulty': 2,
                    'xp_reward': 200,
                    'coin_reward': 20
                },
                {
                    'title': 'Learn Something New',
                    'description': 'Spend 30 minutes learning a new skill.',
                    'difficulty': 3,
                    'xp_reward': 300,
                    'coin_reward': 30
                },
                {
                    'title': 'Exercise Challenge',
                    'description': 'Complete a 20-minute workout session.',
                    'difficulty': 2,
                    'xp_reward': 250,
                    'coin_reward': 25
                }
            ]
