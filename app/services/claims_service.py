rom opensearchpy import OpenSearch
from app.config import OPENSEARCH_HOST
from app.utils.logger import get_logger

logger = get_logger("claims_service")
client = OpenSearch(OPENSEARCH_HOST)

def search_claims(provider_name=None, min_amount=None):
    try:
        logger.info("Searching claims index")

        must = []
        if provider_name:
            must.append({"match": {"provider_name": provider_name}})
        if min_amount:
            must.append({"range": {"claim_amount": {"gte": min_amount}}})

        query = {"query": {"bool": {"must": must}}}
        response = client.search(index="claims", body=query)

        return [hit["_source"] for hit in response["hits"]["hits"]]

    except Exception as e:
        logger.exception("OpenSearch claims query failed")
        raise