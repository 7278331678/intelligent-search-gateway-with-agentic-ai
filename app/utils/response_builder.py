import uuid
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger("response_builder")

def inject_metadata(response: dict):
    try:
        response["meta"]["request_id"] = str(uuid.uuid4())
        response["meta"]["timestamp"] = datetime.utcnow().isoformat()
        return response
    except Exception as e:
        logger.exception("Failed to inject metadata")
        raise