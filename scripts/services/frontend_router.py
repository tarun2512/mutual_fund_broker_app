from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

frontend_router = APIRouter()


@frontend_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "api_login_url": "/user/login",  # Explicit URL
            "api_register_url": "/user/create_user",
            "api_reset_url": "/user/reset_password",
            "route_register": "/register",
            "route_reset_password": "/reset_password",
            "route_funds": "/funds",
        },
    )


@frontend_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "api_login_url": "/user/login",  # Explicit URL
            "api_register_url": "/user/create_user",
            "api_reset_url": "/user/reset_password",
            "route_register": "/register",
            "route_reset_password": "/reset_password",
            "route_login": "/login",
        },
    )


@frontend_router.get("/reset_password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse(
        "auth/reset_password.html",
        {
            "request": request,
            "api_login_url": "/user/login",  # Explicit URL
            "api_register_url": "/user/create_user",
            "api_reset_url": "/user/reset_password",
            "route_register": "/register",
            "route_reset_password": "/reset_password",
            "route_login": "/login",
        },
    )


@frontend_router.get("/funds", response_class=HTMLResponse)
async def funds_page(request: Request):
    return templates.TemplateResponse(
        "auth/funds.html",
        {
            "request": request,
            "api_login_url": "/user/login",  # Explicit URL
            "api_register_url": "/user/create_user",
            "api_reset_url": "/user/reset_password",
            "route_register": "/register",
            "route_reset_password": "/reset_password",
            "route_login": "/login",
        },
    )
