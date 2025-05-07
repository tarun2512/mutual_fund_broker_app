import httpx

from scripts.config import Security
from scripts.db.mongo import mongo_client
from scripts.db.mongo.mutual_fund_store.mutual_fund_data import MutualFundData
from scripts.logging import logger

RAPID_API_URL = "https://latest-mutual-fund-nav.p.rapidapi.com/latest"
RAPID_API_HEADERS = {
    "X-RapidAPI-Key": Security.RAPID_API_KEY,
    "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com",
}


def fetch_nav_value():
    try:
        with httpx.Client() as client:
            response = client.get(RAPID_API_URL, headers=RAPID_API_HEADERS)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"failed to fetch nav value for scheme {str(e)}")


async def update_mutual_fund_family():
    """
    This function updates the mutual fund family details.
    """

    try:
        mutual_fund_data_con = MutualFundData(mongo_client=mongo_client)
        records = await mutual_fund_data_con.find({})
        if not records:
            records = fetch_nav_value()
            await mutual_fund_data_con.insert_many(records)
    except Exception as e:
        logger.error(f"Failed to add MutualFundData: {str(e)}")
