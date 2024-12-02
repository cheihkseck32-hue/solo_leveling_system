from django.core.management.base import BaseCommand
from core.models import ShopItem

class Command(BaseCommand):
    help = 'Populates the store with initial items'

    def handle(self, *args, **kwargs):
        items = [
            {
                'name': 'Training Sword',
                'item_type': 'WEAPON',
                'rarity': 'common',
                'price': 100,
                'description': 'A basic training sword for beginners.',
                'effect': {'strength': 2},
                'icon': 'sword',
            },
            {
                'name': 'Agility Boots',
                'item_type': 'EQUIPMENT',
                'rarity': 'uncommon',
                'price': 250,
                'description': 'Lightweight boots that increase your agility.',
                'effect': {'agility': 3},
                'icon': 'boots',
            },
            {
                'name': 'Wisdom Scroll',
                'item_type': 'CONSUMABLE',
                'rarity': 'rare',
                'price': 500,
                'description': 'A magical scroll that temporarily boosts intelligence.',
                'effect': {'intelligence': 5},
                'icon': 'scroll',
            },
            {
                'name': 'Vitality Crystal',
                'item_type': 'EQUIPMENT',
                'rarity': 'epic',
                'price': 1000,
                'description': 'A crystal that significantly increases your vitality.',
                'effect': {'vitality': 7},
                'icon': 'gem',
            },
            {
                'name': 'Dragon Scale Armor',
                'item_type': 'EQUIPMENT',
                'rarity': 'legendary',
                'price': 2000,
                'description': 'Legendary armor forged from dragon scales.',
                'effect': {'strength': 5, 'vitality': 5},
                'icon': 'shield-alt',
            },
            {
                'name': 'Ancient Tome',
                'item_type': 'EQUIPMENT',
                'rarity': 'epic',
                'price': 1500,
                'description': 'An ancient book containing powerful knowledge.',
                'effect': {'intelligence': 8},
                'icon': 'book',
            },
            {
                'name': 'Swift Dagger',
                'item_type': 'WEAPON',
                'rarity': 'rare',
                'price': 750,
                'description': 'A well-balanced dagger for quick strikes.',
                'effect': {'agility': 4, 'strength': 2},
                'icon': 'khanda',
            },
            {
                'name': 'Health Potion',
                'item_type': 'CONSUMABLE',
                'rarity': 'common',
                'price': 50,
                'description': 'Restores a small amount of health.',
                'effect': {'vitality': 1},
                'icon': 'flask',
            },
            {
                'name': 'Mystic Orb',
                'item_type': 'EQUIPMENT',
                'rarity': 'legendary',
                'price': 2500,
                'description': 'A mysterious orb pulsing with magical energy.',
                'effect': {'intelligence': 6, 'sense': 6},
                'icon': 'circle',
            },
            {
                'name': 'Training Weights',
                'item_type': 'EQUIPMENT',
                'rarity': 'uncommon',
                'price': 300,
                'description': 'Special weights that help build strength.',
                'effect': {'strength': 3},
                'icon': 'dumbbell',
            },
        ]

        for item_data in items:
            ShopItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )
            self.stdout.write(f"Created/Updated item: {item_data['name']}")

        self.stdout.write(self.style.SUCCESS('Successfully populated store items'))
