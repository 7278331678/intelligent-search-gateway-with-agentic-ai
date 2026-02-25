from opensearchpy import OpenSearch
from app.config import OPENSEARCH_HOST
from app.utils.logger import get_logger

logger = get_logger("benefits_service")
client = OpenSearch(OPENSEARCH_HOST)

def search_benefits(plan_id=None):
    try:
        logger.info("Searching benefits index")

        must = []
        if plan_id:
            must.append({"term": {"plan_id": plan_id}})

        query = {"query": {"bool": {"must": must}}}
        response = client.search(index="benefits", body=query)

        return [hit["_source"] for hit in response["hits"]["hits"]]

    except Exception as e:
        logger.exception("OpenSearch benefits query failed")
        raise