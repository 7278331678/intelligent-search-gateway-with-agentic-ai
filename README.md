## AI Search Gateway

AI orchestration layer that turns natural language queries into **governed, schema‑validated JSON** and safe searches against **Elasticsearch / OpenSearch**, using **AWS Bedrock (Claude Sonnet)** for reasoning and tool selection.

### High‑level flow

1. **Client → Lambda**
   - Client sends `POST /ai-search` with JSON body: `{ "query": "Show claims above 10000 for ABC Hospital." }`.
   - API Gateway forwards the request into `handler.lambda_handler`.
2. **Lambda handler**
   - Parses and validates the body.
   - Logs the request with `app.utils.logger`.
   - Calls `app.agent.controller.run_agent(query)` to orchestrate the Bedrock loop and tools.
3. **Bedrock agent loop**
   - System prompt in `app.agent.prompts.SYSTEM_PROMPT` constrains responses to JSON only.
   - Tools are declared in `app.agent.tools_schema.TOOLS` and implemented in:
     - `app.services.claims_service.search_claims`
     - `app.services.providers_service.search_providers`
     - `app.services.benefits_service.search_benefits`
   - `app.bedrock.client.invoke_model` calls the configured Bedrock model (`BEDROCK_MODEL_ID`).
4. **Services → OpenSearch**
   - Services use `opensearch-py` and `OPENSEARCH_HOST` from `app.config` to query the appropriate index.
   - Each service returns domain‑specific JSON conforming to the `app.models.*` Pydantic models.
5. **Validation + response**
   - `app.utils.validator.validate_response_structure` validates the `meta` and `data` sections using:
     - `app.models.meta.Meta`
     - `app.models.claims_models.ClaimsData`
     - `app.models.providers_models.ProvidersData`
     - `app.models.benefits_models.BenefitsData`
   - `app.utils.response_builder.inject_metadata` adds `request_id` and `timestamp`.
   - On error, `app.utils.error.error_response` builds a consistent JSON error envelope.

### Project structure

```text
app/
  agent/
    controller.py      # Bedrock tool-calling loop (run_agent)
    prompts.py         # System prompt / governance rules
    tools_schema.py    # Tool schema passed to the model
  bedrock/
    client.py          # Thin wrapper over bedrock-runtime.invoke_model
  models/
    meta.py            # Meta envelope (domain, total_records, status, ids, timestamps)
    claims_models.py   # ClaimsData/Claim* Pydantic models
    providers_models.py# ProvidersData/Provider* Pydantic models
    benefits_models.py # BenefitsData/Benefit* Pydantic models
  services/
    claims_service.py   # search_claims → OpenSearch "claims" index
    providers_service.py# search_providers → OpenSearch "providers" index
    benefits_service.py # search_benefits → OpenSearch "benefits" index
  utils/
    logger.py           # JSON logger
    validator.py        # validate_response_structure()
    response_builder.py # inject_metadata()
    error.py            # error_response()
  config.py             # BEDROCK_MODEL_ID, AWS_REGION, OPENSEARCH_HOST
  handler.py            # lambda_handler entrypoint used by root handler.py

handler.py               # Root-level re-export for AWS Lambda
docs/
  architecture.md        # Architecture diagram (Mermaid)
```

### Configuration (.env)

Set these environment variables (locally via `.env`, in Lambda via env vars):

- **`BEDROCK_MODEL_ID`**: Bedrock Claude Sonnet model ID  
  e.g. `anthropic.claude-3-sonnet-20240229-v1:0`
- **`AWS_REGION`**: Region for both Bedrock and OpenSearch (e.g. `us-east-1`)
- **`OPENSEARCH_HOST`**: OpenSearch/Elasticsearch endpoint, e.g. `https://your-domain.us-east-1.es.amazonaws.com`

### Local development

1. Create and activate a virtualenv.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with `BEDROCK_MODEL_ID`, `AWS_REGION`, `OPENSEARCH_HOST`.
4. Run a quick local test (pseudo‑code):

```python
from app.handler import lambda_handler

event = {"body": '{"query": "Show claims above 10000 for ABC Hospital."}'}
print(lambda_handler(event, None))
```

### Deployment (AWS Lambda)

- Package the code with dependencies (or use a Lambda container image).
- Set the Lambda handler to `handler.lambda_handler`.
- Configure:
  - IAM permissions for `bedrock:InvokeModel` and `es:ESHttp*` (or OpenSearch equivalent).
  - Environment variables as described above.

