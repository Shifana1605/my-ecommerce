# accounts/elasticsearch_client.py
from elasticsearch import Elasticsearch
from elastic_transport import ConnectionError

index_name = "products"

def get_es_client():
    """Return Elasticsearch client."""
    try:
        # ✅ Correct connection syntax for elasticsearch-py 9.x
        es = Elasticsearch(
            hosts=["http://localhost:9200"],
            verify_certs=False,
            request_timeout=30
        )

        # ✅ Test the connection
        if es.ping():
            print("✅ Connected to Elasticsearch")
            return es
        else:
            print("❌ Could not connect to Elasticsearch (ping failed)")
            return None

    except ConnectionError as e:
        print(f"❌ Elasticsearch connection failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error connecting to Elasticsearch: {e}")
        return None
