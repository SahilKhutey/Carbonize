"""
Main API Router v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints.inference import router as inference_router
from app.api.v1.endpoints.tests import router as tests_router
from app.api.v1.endpoints.predictions import router as predictions_router

api_router = APIRouter()
api_router.include_router(inference_router)
api_router.include_router(tests_router)
api_router.include_router(predictions_router)
