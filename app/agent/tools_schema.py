TOOLS = [
    {
        "name": "search_claims",
        "description": "Search claims index",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider_name": {"type": "string"},
                "min_amount": {"type": "number"}
            }
        }
    },
    {
        "name": "search_providers",
        "description": "Search providers index",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "specialty": {"type": "string"}
            }
        }
    },
    {
        "name": "search_benefits",
        "description": "Search benefits index",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan_id": {"type": "string"}
            }
        }
    }
]