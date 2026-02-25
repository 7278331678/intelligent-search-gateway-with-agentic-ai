rom opensearchpy import OpenSearch
from app.config import OPENSEARCH_HOST
from app.utils.logger import get_logger

logger = get_logger("providers_service")
client = OpenSearch(OPENSEARCH_HOST)

def search_providers(city=None, specialty=None):
    try:
        logger.info("Searching providers index")

        must = []
        if city:
            must.append({"match": {"city": city}})
        if specialty:
            must.append({"match": {"specialty": specialty}})

        query = {"query": {"bool": {"must": must}}}
        response = client.search(index="providers", body=query)

        return [hit["_source"] for hit in response["hits"]["hits"]]

    except Exception as e:
        logger.exception("OpenSearch providers query failed")
        raise