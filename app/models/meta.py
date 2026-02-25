from pydantic import BaseModel


class Meta(BaseModel):
    domain: str
    total_records: int
    status: str
    request_id: str | None = None
    timestamp: str | None = None