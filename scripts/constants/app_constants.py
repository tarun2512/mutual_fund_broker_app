class APIEndpoints:
    # Base Proxies
    proxy_user = "/user"
    proxy_funds = "/funds"

    # Login & Register user API's
    api_login = "/login"
    api_logout = "/logout"
    api_reset_password = "/reset_password"
    api_create_user = "/create_user"

    # mutual fund API's
    api_add_funds = "/add_funds"
    api_fetch_funds = "/fetch_funds"
    api_fetch_mutual_fund_family_data = "/fetch_mutual_fund_family_data"
    api_fetch_hourly_portfolio_data = "/fetch_hourly_portfolio_data"


class Secrets:
    LOCK_OUT_TIME_MINS = 30
    leeway_in_mins = 10
    unique_key = "45c37939-0f75"
    token = "8674cd1d-2578-4a62-8ab7-d3ee5f9a"
    alg = "RS256"
