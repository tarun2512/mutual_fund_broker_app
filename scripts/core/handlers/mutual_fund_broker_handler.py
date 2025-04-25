import time
import httpx

from scripts.config import Security
from scripts.core.engine.user_handler_helper import UserHandlerHelper
from scripts.db.mongo import mongo_client
from scripts.db.mongo.mutual_fund_store.mutual_fund_data import MutualFundData
from scripts.db.mongo.mutual_fund_store.user_portfolio import UserPortfolio, UserPortfolioSchema
from scripts.db.mongo.mutual_fund_store.user_portfolio_hourly import UserPortfolioHourly
from scripts.db.mongo.user_meta_store.user_collection import User
from scripts.db.redis_connection import login_db
from scripts.logging import logger
from scripts.schemas.mutual_fund_broker_schema import AddFunds
from scripts.utils.common_utils import CommonUtils


class MutualFundBrokerHandler:
    def __init__(self):
        self.user_con = User(mongo_client=mongo_client)
        self.user_handler_helper = UserHandlerHelper()
        self.common_utils = CommonUtils()
        self.login_redis = login_db
        self.user_portfolio_con = UserPortfolio(mongo_client)
        self.mutual_fund_data_con = MutualFundData(mongo_client=mongo_client)
        self.user_portfolio_hourly_con = UserPortfolioHourly(mongo_client=mongo_client)
        self.rapid_api_url = "https://latest-mutual-fund-nav.p.rapidapi.com/latest"
        self.rapid_api_headers = {
            "X-RapidAPI-Key": Security.RAPID_API_KEY,
            "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com",
        }

    def fetch_nav_value(self, scheme_code):
        try:
            with httpx.Client() as client:
                response = client.get(self.rapid_api_url, params={"Scheme_Code": scheme_code}, headers=self.rapid_api_headers)
                response.raise_for_status()
                nav_value = response.json()[0].get('Net_Asset_Value')
                return nav_value
        except Exception as e:
            logger.error(f"failed to fetch nav value for scheme {str(e)}")

    def add_funds_to_portfolio(self, request_data: AddFunds):
        try:
            fetch_user_portfolio = self.user_portfolio_con.find_user_portfolio(user_id=request_data.user_id, scheme_code=
                                                                               request_data.scheme_code)
            request_data.nav = self.fetch_nav_value(request_data.scheme_code)
            if not fetch_user_portfolio:
                units_held = request_data.amount / request_data.nav
                portfolio_record = UserPortfolioSchema(
                user_id=request_data.user_id,
                scheme_code=request_data.scheme_code,
                scheme_name=request_data.scheme_name,
                units_held=units_held,
                last_investment_on=int(time.time() * 1000),
                average_nav_price=request_data.nav,
                mutual_fund_family=request_data.mutual_fund_family)
                self.user_portfolio_con.update_user_portfolio({}, data=portfolio_record.model_dump())
            else:
                updated_units_held = fetch_user_portfolio.get('units_held', 0) + request_data.amount / request_data.nav
                average_nav_price = (fetch_user_portfolio.get('average_nav_price', 0) + request_data.nav)/2
                self.user_portfolio_con.update_user_portfolio(query={"user_id":request_data.user_id}, data={
                    "units_held": updated_units_held, "average_nav_price": average_nav_price, "last_investment_on":int(time.time() * 1000)
                })
        except Exception as e:
            logger.exception(f"failed to add funds {str(e)}")

    def fetch_user_portfolio(self, user_id):
        try:
            records = list(self.user_portfolio_con.find_user_portfolio(user_id=user_id))
            for record in records:
                record["current_nav_price"] = self.fetch_nav_value(record.get("scheme_code"))
            return records

        except Exception as e:
            logger.error(f"failed to fetch user portfolio {str(e)}")

    def fetch_mutual_fund_family_data(self):
        try:
            records = self.mutual_fund_data_con.fetch_records()
            mutual_fund_data = []
            for record in records:
                mutual_fund_data.append({
                    "scheme_code": record.get("Scheme_Code"),
                    "scheme_name": record.get("Scheme_Name"),
                    "fund_family": record.get("Mutual_Fund_Family"),
                })
            return mutual_fund_data
        except Exception as e:
            logger.error(f"failed to fetch {str(e)}")

    def fetch_hourly_portfolio_data(self, user_id: str) -> dict[str, dict]:
        """
        Return a dict where each key is the hourly `timestamp`
        and the value is a mapping scheme_code → { nav, value, …original fund meta }.
        """
        try:
            # ---- 1. DB reads ----------------------------------------------------
            user_portfolio = self.user_portfolio_con.find_user_portfolio(user_id=user_id)
            hourly_snapshots = self.user_portfolio_hourly_con.find_user_portfolio_hourly(user_id=user_id)

            # ---- 2. Constant‑time lookup table for user's funds -----------------
            # {scheme_code: fund_meta_dict}
            portfolio_lookup = {f["scheme_code"]: f for f in user_portfolio}

            # ---- 3. Build response ---------------------------------------------
            result: dict[str, dict] = {}

            for snapshot in hourly_snapshots:
                ts = snapshot["timestamp"]  # assuming always present
                bucket = result.setdefault(ts, {})  # create per‑hour dict once

                for inv in snapshot.get("investments", []):
                    scode = inv["scheme_code"]
                    if scode in portfolio_lookup:  # include only user’s funds
                        bucket[scode] = {
                            "nav": inv["nav"],
                            "value": inv["value"],
                            **portfolio_lookup[scode]  # merge static fund details
                        }

            return result

        except Exception as e:
            logger.exception(f"Failed to fetch hourly portfolio data {str(e)}")
            raise  # surface the error; caller can handle
