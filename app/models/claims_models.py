class ClaimFinancial(BaseModel):
    currency: Optional[str] = "USD"


class ClaimDates(BaseModel):
    submission_date: str
    processed_date: Optional[str] = None


class ClaimItem(BaseModel):
    claim_id: str
    member: ClaimMember
    provider: ClaimProvider
    financial: ClaimFinancial
    dates: ClaimDates
    status: str


class ClaimsData(BaseModel):
    claims: List[ClaimItem]