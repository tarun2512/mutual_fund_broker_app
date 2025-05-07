from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Response

from scripts.config import Security
from scripts.constants.app_constants import APIEndpoints
from scripts.core.handlers.user_handler import UserHandler
from scripts.errors import (
    CustomError,
    LicenceValidationError,
    FixedDelayError,
    VariableDelayError,
    TooManyRequestsError,
)
from scripts.errors.exception_codes import DefaultExceptionsCode
from scripts.logging import logger
from scripts.schemas.response_models import (
    DefaultFailureResponse,
    DefaultResponse,
    DefaultSuccessResponse,
)
from scripts.schemas.user_schema import (
    UserRegister,
    LoginRequest,
    ResetPasswordRequest,
)

user_router = APIRouter(prefix=APIEndpoints.proxy_user, tags=["User Service"])


@user_router.post(
    APIEndpoints.api_create_user, response_model=DefaultResponse, name="create_user"
)
async def create_user(
    request_data: UserRegister,
):
    """
    API to save the user
    """
    try:
        user_handler = UserHandler()
        response = await user_handler.register_user(request_data)
        return DefaultSuccessResponse(
            message="User registered successfully",
            data=response,
        ).model_dump()

    except CustomError as e:
        return DefaultFailureResponse(error=str(e)).model_dump()
    except Exception as e:
        logger.exception(f"Exception in create_user: {e}")
        return DefaultFailureResponse(
            message="Failed while creating user", error=str(e)
        ).model_dump()


@user_router.post(
    APIEndpoints.api_reset_password, include_in_schema=False, name="reset_password"
)
async def reset_password(request_data: ResetPasswordRequest, request: Request):
    """
    This is the service to re-set the password via email  from the portal
    :return: Base64 encoded JSON with status success or failed
    """
    try:
        user_handler = UserHandler()
        resp = await user_handler.reset_password(request_data.model_dump())
        resp.set_cookie("captcha_cookie", "", expires=0, secure=Security.SECURE_COOKIE)
        resp.set_cookie("captcha-string", "", expires=0, secure=Security.SECURE_COOKIE)
        return resp
    except Exception as e:
        logger.exception(str(e))
        return str(e)


@user_router.post(APIEndpoints.api_login)
async def login(
    request_data: LoginRequest,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
):
    """
    This API is used to validate the username and password and provide required authentication to the user
    """
    try:
        logger.info(
            f"HOST - {request.client.host}\nHOST - {request.headers.get('host')}"
        )
        user_handler = UserHandler()
        resp = await user_handler.login_flow(
            login_request=request_data,
            request=request,
            response=response,
            bg_task=background_tasks,
        )
        return {
            "status": "success",
            "message": "Successfully Logged in",
            "data": resp,
        } or {"status": "failed", "message": DefaultExceptionsCode.DE001}
    except LicenceValidationError as e:
        return {"status": "failed", "message": str(e)}
    except (FixedDelayError, VariableDelayError) as e:
        return {"status": "failed", "message": str(e)}
    except TooManyRequestsError as e:
        raise HTTPException(
            status_code=429,
            detail=e.args,
        )
    except Exception as e:
        logger.exception(f"Error while logging - f{str(e)}")
        raise HTTPException(
            status_code=401,
            detail=e.args,
        ) from e


@user_router.post(APIEndpoints.api_logout)
async def logout(request: Request):
    """
    API to log out the user session of the logged-in user
    """
    try:
        session_id = request.cookies.get("session_id")
        login_token = request.cookies.get("login-token")
        if login_token is None:
            login_token = request.headers.get("login-token")
        refresh_token = request.cookies.get("refresh-token")
        if refresh_token is None:
            refresh_token = request.headers.get("refresh-token")
        user_handler = UserHandler()
        return await user_handler.logout(session_id, login_token, refresh_token)
    except Exception as e:
        return DefaultFailureResponse(
            message="Failed to logout", error=str(e)
        ).model_dump()
