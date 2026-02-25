## Architecture Diagram

```mermaid
flowchart LR
    subgraph Client
        U[User / Client App]
    end

    subgraph AWS["AWS Cloud"]
        APIGW[API Gateway<br/>/ai-search endpoint]
        L[Lambda<br/>handler.lambda_handler]

        subgraph App["AI Search Gateway (Lambda code)"]
            H[app/handler.py<br/>request parsing]
            A[app/agent/controller.py<br/>Bedrock agent loop]
            P[app/agent/prompts.py<br/>system rules]
            T[app/agent/tools_schema.py<br/>tool schema]

            subgraph Svc["Service Layer (app/services)"]
                C[claims_service.search_claims]
                PR[providers_service.search_providers]
                B[benefits_service.search_benefits]
            end

            subgraph Models["Models (app/models)"]
                MMeta[meta.Meta]
                MC[claims_models.ClaimsData]
                MP[providers_models.ProvidersData]
                MB[benefits_models.BenefitsData]
            end

            subgraph Utils["Utils (app/utils)"]
                LG[logger]
                VL[validator]
                RB[response_builder]
                ER[error]
            end

            BR[app/bedrock/client.py<br/>Bedrock Runtime]
        end

        OS[(OpenSearch / Elasticsearch)]
        BRW[(AWS Bedrock<br/>Claude Sonnet)]
    end

    U -->|HTTP POST /ai-search| APIGW --> L --> H
    H --> A
    A --> BR --> BRW
    A -->|tool: search_claims| C --> OS
    A -->|tool: search_providers| PR --> OS
    A -->|tool: search_benefits| B --> OS

    A --> Models
    A --> Utils
    H --> Utils

    OS --> A
    A --> H --> U
```

This diagram shows the full path from **client query** → **Lambda** → **Bedrock‑driven tool orchestration** → **OpenSearch domain services** → **governed JSON response** back to the caller.

