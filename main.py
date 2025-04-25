import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from scripts.constants import AppSpec
from scripts.core.engine.background_task import update_mutual_fund_family
from scripts.services import router
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware


from scripts.services.frontend_router import frontend_router
from scripts.services.mutual_fund_broker_services import fund_router
from scripts.services.user_service import user_router

app = FastAPI(
    title=AppSpec.name,
    description=AppSpec.description,
    summary=AppSpec.summary,
    version="7.09",
    root_path="/form-mt",
)

# Add this before mounting any routes
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",  # Use a strong secret key in production
    session_cookie="session_cookie",
)

if os.environ.get("ENABLE_CORS") in (True, "true", "True") and os.environ.get("CORS_URLS"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.environ.get("CORS_URLS").split(","),
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "PUT"],
        allow_headers=["*"],
    )

app.include_router(router)
app.include_router(user_router)
app.include_router(frontend_router)
app.include_router(fund_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    # Run once immediately
    update_mutual_fund_family()
