import os

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from apiserver.routes.auth_route import AuthRouter
from apiserver.routes.project_route import ProjectRouter


app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: only allow origins from frontend in future
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

auth_router = AuthRouter()
app.include_router(auth_router.router, prefix='/apiserver')

project_router = ProjectRouter()
app.include_router(project_router.router, prefix='/apiserver')


@app.get("/apiserver")
async def root():
    return {"message": "Wilkins Dashboard"}
