import json
from app.agent.controller import run_agent
from app.utils.validator import validate_response_structure
from app.utils.response_builder import inject_metadata
from app.utils.error import error_response
from app.utils.logger import get_logger

logger = get_logger("handler")


def lambda_handler(event, context):
    try:
        logger.info("Received event")

        body = parse_body(event)
        user_query = body.get("query")

        if not user_query:
            logger.error("Missing query in request body")
            return error_response(400, "Missing query")

        logger.info(f"Processing query: {user_query}")

        result = run_agent(user_query)
        result = validate_response_structure(result)
        result = inject_metadata(result)

        # 👇 include original query in response
        response_payload = {
            "query": user_query,
            "result": result
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_payload)
        }

    except ValueError as ve:
        logger.warning(str(ve))
        return error_response(400, str(ve))

    except Exception as e:
        logger.exception("Unhandled exception in lambda_handler")
        return error_response(500, "Internal server error", {"error": str(e)})