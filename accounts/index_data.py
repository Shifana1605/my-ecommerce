from accounts.elasticsearch_client import es  # ✅ correct import path
from accounts.models import Product
from django.conf import settings

def index_products():
    print("✅ Connected to Elasticsearch")

    # Delete existing index if any (optional)
    if es.indices.exists(index="products"):
        es.indices.delete(index="products")

    # Create new index
    es.indices.create(index="products", ignore=400)

    # Index all products
    for product in Product.objects.all():
        doc = {
            "id": product.id,
            "product_name": product.product_name,
            "category": product.category.category_name if product.category else None,
            "mrp_price": float(product.mrp_price),
            "discount_price": float(product.discount_price),
            "quantity": product.quantity,
        }
        es.index(index="products", id=product.id, document=doc)

    print("✅ Products indexed successfully!")
