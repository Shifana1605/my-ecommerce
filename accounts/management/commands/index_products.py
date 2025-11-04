# accounts/management/commands/index_products.py
from django.core.management.base import BaseCommand
from accounts.models import Product
from accounts.elasticsearch_client import get_es_client

class Command(BaseCommand):
    help = "Indexes all products into Elasticsearch"

    def handle(self, *args, **kwargs):
        es = get_es_client()
        if not es:
            self.stdout.write(self.style.ERROR("❌ Elasticsearch not connected. Please start the ES server."))
            return

        products = Product.objects.all()
        self.stdout.write(f"Indexing {products.count()} products...")

        for product in products:
            doc = {
    "id": product.id,
    "name": getattr(product, "product_name", None),
    "description": getattr(product, "description", ""),
    "price": float(getattr(product, "mrp_price", 0)),
    "category": getattr(product.category, "category_name", ""),
}

            es.index(index="products", id=product.id, document=doc)

        self.stdout.write(self.style.SUCCESS("✅ Products indexed successfully!"))
