"""
API v1ルーター

APIバージョン1のすべてのエンドポイントを統合
"""
from fastapi import APIRouter
from app.api.v1.endpoints import custom_master
from app.api.v1.endpoints import inventory

api_router = APIRouter()

# 得意先マスタAPIを追加
api_router.include_router(custom_master.router)

# 工場マスタAPIを追加
api_router.include_router(inventory.router)

