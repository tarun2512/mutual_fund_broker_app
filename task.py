from datetime import datetime, timezone

import httpx
from celery_app import celery_app

from scripts.config import Security
from scripts.db.mongo import mongo_client
from scripts.db.mongo.mutual_fund_store.user_portfolio import UserPortfolio
from scripts.db.mongo.mutual_fund_store.user_portfolio_hourly import UserPortfolioHourly
from scripts.db.mongo.user_meta_store.user_collection import User
from scripts.logging import logger


class UpdateHourlyPortfolio:
    def __init__(self):
        self.user_con = User(mongo_client=mongo_client)
        self.user_portfolio_con = UserPortfolio(mongo_client)
        self.user_portfolio_hourly_con = UserPortfolioHourly(mongo_client=mongo_client)
        self.rapid_api_url = "https://latest-mutual-fund-nav.p.rapidapi.com/latest"
        self.rapid_api_headers = {
            "X-RapidAPI-Key": Security.RAPID_API_KEY,
            "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com",
        }

    def get_nav_for_scheme(self, scheme_code):
        try:
            with httpx.Client() as client:
                response = client.get(self.rapid_api_url, params={"Scheme_Code": scheme_code}, headers=self.rapid_api_headers)
                response.raise_for_status()
                nav_value = response.json()[0].get('Net_Asset_Value')
                return nav_value
        except Exception as e:
            logger.error(f"failed to fetch nav value for scheme {str(e)}")

    def update_funds(self):
        try:
            users = self.user_con.distinct("user_id")

            for user_id in users:
                user_portfolio = list(self.user_portfolio_con.find({"user_id": user_id}))

                investments = []
                total_value = 0

                for scheme in user_portfolio:
                    nav = self.get_nav_for_scheme(scheme['scheme_code'])
                    value = scheme['units_held'] * nav

                    investments.append({
                        "scheme_code": scheme['scheme_code'],
                        "nav": round(nav, 4),
                        "value": round(value, 2)
                    })

                    total_value += value

                result = {
                    "user_id": user_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_value": round(total_value, 2),
                    "investments": investments
                }

                # Insert hourly snapshot
                self.user_portfolio_hourly_con.insert_one(result)
                print(f"Inserted hourly portfolio for user {user_id}")
        except Exception as e:
            logger.error(f"{str(e)}")

@celery_app.task
def my_hourly_function():
    print(f"✅ Running task at {datetime.utcnow()}")
    UpdateHourlyPortfolio().update_funds()


