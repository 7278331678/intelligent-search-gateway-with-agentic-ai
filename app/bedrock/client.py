import boto3
import json
from app.config import BEDROCK_MODEL_ID, AWS_REGION
from app.utils.logger import get_logger

logger = get_logger("bedrock_client")

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def invoke_model(messages, tools):
    try:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": messages,
            "tools": tools
        }

        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(body)
        )

        return json.loads(response["body"].read())

    except Exception as e:
        logger.exception("Failed to invoke Bedrock model")
        raise