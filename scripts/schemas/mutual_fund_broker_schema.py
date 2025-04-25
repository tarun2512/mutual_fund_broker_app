from pydantic import BaseModel, EmailStr, constr, validator, Field
from typing import Optional

class AddFunds(BaseModel):
    user_id: str
    amount: int
    mutual_fund_family: str
    scheme_name: str
    scheme_code: int
    transaction_date: str
    nav: Optional[float] = 0


class FetchPortfolio(BaseModel):
    user_id: str


class TrackInvestmentValue(BaseModel):
    user_id: str


class FetchMutualFundData(BaseModel):
    mutual_fund_family: str
    scheme_name: str