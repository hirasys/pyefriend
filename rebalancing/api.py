"""
RUN command in source:
    uvicorn rebalancing.api:app --reload
"""
import os

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html

from rebalancing.settings import BASE_DIR
from rebalancing.app.auth import r as auth_router
from rebalancing.app.router import r as app_router

# rebalance app info
title = 'Re-Balancing App'
description = f"""
##### FastAPI PID: {os.getpid()}
""" + open(os.path.join(BASE_DIR, 'DESCRIPTION.md'), 'utf-8').read()

# create app
app = FastAPI(title=title,
              description=description,
              version='v1',
              debug=True,
              docs_url=None,
              redoc_url=None)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# docs
@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# redocs
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{title} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.exception_handler(RequestValidationError)
async def auth_exception_handler(request: Request, exc: RequestValidationError):
    msg = exc.errors()[0].get('msg')
    print('validation error:', msg)
    print('exc.body: ', exc.body)
    return JSONResponse(content={'detail': msg}, status_code=status.HTTP_400_BAD_REQUEST)

app.include_router(auth_router)
app.include_router(app_router)
