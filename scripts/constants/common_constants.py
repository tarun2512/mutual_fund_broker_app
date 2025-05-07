class CommonStatusCode:
    SUCCESS_CODES = (
        200,
        201,
        204,
    )


class CommonKeys:
    KEY_USER_ID = "user_id"

    KEY_CREATED_BY = "created_by"
    KEY_CREATED_TIME = "created_at"
    KEY_COMPLETED_AT = "completed_at"
    KEY_UPDATED_AT = "updated_by"
    KEY_LAST_UPDATED_TIME = "updated_at"


class STATUS:
    SUCCESS = "success"
    FAILED = "failed"
    SUCCESS_CODES = [200, 201]


class DefaultResponseMessages:
    USER_UNAUTHORIZED = "User Unauthorized"
    VALUE_SUCCESS = "success"
    VALUE_FAILED = "failed"
    VALUE_UNDEFINED = "undefined"


class Secrets:
    LOCK_OUT_TIME_MINS = 30
    leeway_in_mins = 10
    unique_key = "45c37939-0f75"
    token = "8674cd1d-2578-4a62-8ab7-d3ee5f9a"
    issuer = "ilens"
    alg = "RS256"
    signature_key = "Assignment"
    signature_key_alg = ["HS256"]
