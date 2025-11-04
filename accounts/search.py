# accounts/search.py
from .elasticsearch_client import get_es_client, index_name

def search_products(query=None, category=None, min_price=None, max_price=None):
    """Search products using Elasticsearch."""
    es = get_es_client()
    if not es:
        print("❌ Elasticsearch client not available")
        return []

    must_clauses = []

    if query:
        must_clauses.append({
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description", "category"]
                
            }
        })

    if category:
        must_clauses.append({"match": {"category": category}})

    if min_price or max_price:
        price_range = {}
        if min_price:
            price_range["gte"] = float(min_price)
        if max_price:
            price_range["lte"] = float(max_price)
        must_clauses.append({"range": {"price": price_range}})

    search_body = {
        "query": {
            "bool": {
                "must": must_clauses if must_clauses else [{"match_all": {}}]
            }
        }
    }

    response = es.search(index=index_name, body=search_body)

    hits = response.get("hits", {}).get("hits", [])
    results = [hit["_source"] for hit in hits]

    print(f"✅ Found {len(results)} results")
    return results
