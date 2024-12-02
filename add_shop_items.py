import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solo_leveling_system.settings')
django.setup()

from core.models import ShopItem

# Clear existing items
ShopItem.objects.all().delete()

# Create new items
items = [
    # Health & Fitness Items
    {
        'name': 'Training Weights',
        'description': 'Ancient weighted training gear that increases strength',
        'price': 100,
        'rarity': 'COMMON',
        'item_type': 'EQUIPMENT',
        'category': 'health',
        'stat_type': 'strength',
        'stat_increase': 2,
        'icon': 'dumbbell'
    },
    {
        'name': 'Swift Runner\'s Boots',
        'description': 'Enchanted boots that enhance agility',
        'price': 200,
        'rarity': 'UNCOMMON',
        'item_type': 'EQUIPMENT',
        'category': 'health',
        'stat_type': 'agility',
        'stat_increase': 3,
        'icon': 'running'
    },
    # Education Items
    {
        'name': 'Ancient Tome of Knowledge',
        'description': 'A mystical book that greatly increases intelligence',
        'price': 500,
        'rarity': 'EPIC',
        'item_type': 'CONSUMABLE',
        'category': 'education',
        'stat_type': 'intelligence',
        'stat_increase': 5,
        'icon': 'book'
    },
    # Career Items
    {
        'name': 'Professional\'s Monocle',
        'description': 'Enhances perception and analytical abilities',
        'price': 300,
        'rarity': 'RARE',
        'item_type': 'EQUIPMENT',
        'category': 'career',
        'stat_type': 'sense',
        'stat_increase': 4,
        'icon': 'glasses'
    },
    # Personal Development
    {
        'name': 'Heart of the Warrior',
        'description': 'A legendary artifact that significantly boosts vitality',
        'price': 1000,
        'rarity': 'LEGENDARY',
        'item_type': 'EQUIPMENT',
        'category': 'personal',
        'stat_type': 'vitality',
        'stat_increase': 7,
        'icon': 'heart'
    },
    # Creative Items
    {
        'name': 'Artist\'s Inspiration',
        'description': 'Enhances creative thinking and intelligence',
        'price': 250,
        'rarity': 'UNCOMMON',
        'item_type': 'CONSUMABLE',
        'category': 'creative',
        'stat_type': 'intelligence',
        'stat_increase': 3,
        'icon': 'paint-brush'
    },
    # Social Items
    {
        'name': 'Charm of Charisma',
        'description': 'Boosts social awareness and perception',
        'price': 400,
        'rarity': 'RARE',
        'item_type': 'EQUIPMENT',
        'category': 'social',
        'stat_type': 'sense',
        'stat_increase': 4,
        'icon': 'comments'
    },
    # Financial Items
    {
        'name': 'Merchant\'s Wisdom',
        'description': 'Increases intelligence for better financial decisions',
        'price': 350,
        'rarity': 'RARE',
        'item_type': 'CONSUMABLE',
        'category': 'financial',
        'stat_type': 'intelligence',
        'stat_increase': 4,
        'icon': 'chart-line'
    },
    # Health & Fitness (Advanced)
    {
        'name': 'Olympian\'s Belt',
        'description': 'A powerful artifact that enhances both strength and agility',
        'price': 800,
        'rarity': 'EPIC',
        'item_type': 'EQUIPMENT',
        'category': 'health',
        'stat_type': 'strength',
        'stat_increase': 6,
        'icon': 'medal'
    },
    # Personal Development (Advanced)
    {
        'name': 'Soul Crystal',
        'description': 'A mystical crystal that enhances overall vitality',
        'price': 600,
        'rarity': 'EPIC',
        'item_type': 'EQUIPMENT',
        'category': 'personal',
        'stat_type': 'vitality',
        'stat_increase': 5,
        'icon': 'gem'
    },
]

# Create items
for item_data in items:
    ShopItem.objects.create(**item_data)

print("Successfully added all shop items!")
