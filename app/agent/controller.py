import json
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools_schema import TOOLS
from app.bedrock.client import invoke_model
from app.services.benefits_service import search_benefits
from app.services.providers_service import search_providers
from app.services.claims_service import search_claims
from app.utils.logger import get_logger

logger = get_logger("agent_controller")


def run_agent(user_query):
    logger.info(f"Agent received query: {user_query}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    while True:
        try:
            response = invoke_model(messages, TOOLS)
            output = response["content"][0]
            logger.info(f"LLM output: {output}")

        except Exception as e:
            logger.exception("Error calling Bedrock")
            raise

        if output["type"] == "tool_use":
            tool_name = output["name"]
            tool_input = output["input"]

            logger.info(f"Tool requested: {tool_name} input: {tool_input}")

            try:
                if tool_name == "search_claims":
                    result = search_claims(**tool_input)
                elif tool_name == "search_providers":
                    result = search_providers(**tool_input)
                elif tool_name == "search_benefits":
                    result = search_benefits(**tool_input)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

            except Exception as e:
                logger.exception("Tool execution failed: {tool_name}")
                raise

            messages.append({
                "role": "assistant",
                "content": [output]
            })

            message.append({
                "role": "user",
                "content": [{"type": "tool_result", 
                "tool_use_id": output["id"], 
                "content": json.dumps(result)
                }]
            })
        
        else::
            try:
                final_result = json.loads(output["text"])
                logger.info(f"Agent returned final result")
                return final_result
            except Exception as e:
                logger.exception("Failed to parse final result")
                raise










