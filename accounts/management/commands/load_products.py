from django.core.management.base import BaseCommand
from accounts.models import Category, Product
import json
#Category and product services
class Command(BaseCommand):
    help = 'Load products data from JSON file'

    def handle(self, *args, **kwargs):
        with open('accounts/products.json', 'r') as f:
            data = json.load(f)
        
        for category_data in data:
            category_name = category_data['category']
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Category '{category_name}' not found."))
                continue

            for product in category_data['products']:
                Product.objects.create(
                    category=category,
                    name=product['name'],
                    mrp_price=product['mrp_price'],
                    discount_price=product['discount_price'],
                    quantity=product['quantity']
                )
        self.stdout.write(self.style.SUCCESS('Products loaded successfully!'))
