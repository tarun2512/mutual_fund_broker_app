from fastapi import APIRouter

from scripts.constants.app_constants import APIEndpoints
from scripts.core.handlers.mutual_fund_broker_handler import MutualFundBrokerHandler
from scripts.logging import logger
from scripts.schemas.mutual_fund_broker_schema import AddFunds
from scripts.schemas.response_models import (
    DefaultFailureResponse,
    DefaultSuccessResponse,
)

fund_router = APIRouter(prefix=APIEndpoints.proxy_funds, tags=["User Service"])


@fund_router.post(APIEndpoints.api_add_funds, status_code=201)
async def add_funds(request_data: AddFunds):
    """Add a scheme to the authenticated user's portfolio.
    payload expects {"scheme_code": str, "amount": float, "nav": float .. }
    """
    try:
        fund_broker_handler_handler = MutualFundBrokerHandler()
        await fund_broker_handler_handler.add_funds_to_portfolio(request_data)
        return DefaultSuccessResponse(message="Funds Added Successfully", data={})
    except Exception as e:
        logger.error(f"failed to add funds to portfolio, {str(e)}")
        return DefaultFailureResponse(message="Failed to add funds to portfolio")


@fund_router.get(APIEndpoints.api_fetch_funds)
async def fetch_user_portfolio(user_id: str):
    """Return open‑ended schemes for a chosen fund family."""
    try:
        fund_broker_handler_handler = MutualFundBrokerHandler()
        records = await fund_broker_handler_handler.fetch_user_portfolio(
            user_id=user_id
        )
        return DefaultSuccessResponse(
            message="Portfolio fetched successfully", data=records
        )
    except Exception as e:
        logger.error(f"failed to fetch mutual_fund_data {str(e)}")
        return DefaultFailureResponse(message="Failed to fetch portfolio", data=[])


@fund_router.get(APIEndpoints.api_fetch_mutual_fund_family_data)
async def fetch_mutual_fund_family_data():
    """Return open‑ended schemes for a chosen fund family."""
    try:
        fund_broker_handler_handler = MutualFundBrokerHandler()
        records = await fund_broker_handler_handler.fetch_mutual_fund_family_data()
        return DefaultSuccessResponse(
            message="Mutual Fund Family Data fetched successfully", data=records
        )
    except Exception as e:
        logger.error(f"failed to fetch mutual_fund_data {str(e)}")
        return DefaultFailureResponse(
            message="Failed to fetch Mutual Fund Family Data", data=[]
        )


@fund_router.get(APIEndpoints.api_fetch_hourly_portfolio_data)
async def fetch_hourly_portfolio_data(user_id: str):
    """Return open‑ended schemes for a chosen fund family."""
    try:
        fund_broker_handler_handler = MutualFundBrokerHandler()
        return await fund_broker_handler_handler.fetch_hourly_portfolio_data(user_id)
    except Exception as e:
        logger.error(f"failed to fetch mutual_fund_data {str(e)}")
