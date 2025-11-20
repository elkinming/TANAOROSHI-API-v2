"""
API v1ルーター

APIバージョン1のすべてのエンドポイントを統合
"""
from fastapi import APIRouter
from app.api.v1.endpoints import custom_master

api_router = APIRouter()

# 得意先マスタAPIを追加
api_router.include_router(custom_master.router)

