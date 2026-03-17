from fastapi import FastAPI
from api.endpoints.test import router as test_router

app = FastAPI()

app.include_router(test_router)
