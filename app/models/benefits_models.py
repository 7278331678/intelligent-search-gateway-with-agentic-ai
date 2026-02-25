from pydantic import BaseModel
from typing import List, Optional


class BenefitCoverage(BaseModel):
    percentage: float
    annual_limit: Optional[float] = None
    currency: Optional[str] = "USD"


class BenefitEligibility(BaseModel):
    waiting_period_days: Optional[int] = None
    preauthorization_required: Optional[bool] = False


class BenefitItem(BaseModel):
    plan_id: str
    benefit_type: str
    coverage: BenefitCoverage
    eligibility: BenefitEligibility


class BenefitsData(BaseModel):
    benefits: List[BenefitItem]