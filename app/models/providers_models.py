rom pydantic import BaseModel
from typing import List


class ProviderLocation(BaseModel):
    city: str
    state: str


class ProviderNetwork(BaseModel):
    status: str
    effective_date: str


class ProviderItem(BaseModel):
    provider_id: str
    provider_name: str
    location: ProviderLocation
    specialty: str
    network: ProviderNetwork


class ProvidersData(BaseModel):
    providers: List[ProviderItem]