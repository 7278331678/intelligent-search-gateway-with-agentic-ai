import json
from app.utils.logger import get_logger

logger = get_logger("error")

def error_response(status_code: int, message: str, details: dict = None):
    body = {
        "meta": {
            "domain": "unknown",
            "total_records": 0,
            "status": "error"
        },
        "data": {},
        "summary": message
    }

    if details:
        body["details"] = details

    logger.error(f"Error response: {status_code} - {message} - {details}")

    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }