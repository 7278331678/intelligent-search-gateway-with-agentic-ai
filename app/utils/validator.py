from app.models.meta import Meta
from app.models.claims_models import ClaimsData
from app.models.providers_models import ProvidersData
from app.models.benefits_models import BenefitsData
from app.utils.logger import get_logger

logger = get_logger("validator")


def validate_response_structure(response: dict):
    try:
        if "meta" not in response or "data" not in response:
            raise ValueError("Missing meta or data")

        # validate meta structure
        Meta(**response["meta"])

        domain = response["meta"]["domain"]

        if domain == "claims":
            ClaimsData(**response["data"])

        elif domain == "providers":
            ProvidersData(**response["data"])

        elif domain == "benefits":
            BenefitsData(**response["data"])

        else:
            raise ValueError("Unknown domain")

        return response

    except Exception as e:
        logger.exception("Response validation failed")
        raise