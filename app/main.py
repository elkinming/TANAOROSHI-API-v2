"""
FastAPIアプリケーションエントリーポイント

FastAPIアプリケーションの初期化と設定
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.api.v1.api import api_router
from app.api.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.utils.logger import setup_logging, get_logger

# ログ設定を初期化
setup_logging(
    log_level=settings.log_level,
    log_file=settings.log_file,
    max_bytes=settings.log_max_bytes,
    backup_count=settings.log_backup_count,
    when=settings.log_when
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理

    Args:
        app: FastAPIアプリケーションインスタンス
    """
    # 起動時の処理
    logger.info(f"アプリケーション起動: {settings.api_title} v{settings.api_version}")
    logger.info(f"環境: {settings.environment.value}")

    yield

    # 終了時の処理
    logger.info("アプリケーション終了")


# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
    root_path=settings.api_root_path,
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.get_cors_methods_list(),
    allow_headers=settings.get_cors_headers_list(),
)

# 例外ハンドラーを登録
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# APIルーターを追加
app.include_router(api_router)


@app.get("/health", tags=["ヘルスチェック"])
async def health_check():
    """
    ヘルスチェックエンドポイント

    Returns:
        dict: アプリケーションの状態
    """
    return {
        "status": "healthy",
        "environment": settings.environment.value,
        "version": settings.api_version
    }


@app.get("/", tags=["ルート"])
async def root():
    """
    ルートエンドポイント

    Returns:
        dict: API情報
    """
    return {
        "message": "Tanaoroshi Backend API",
        "version": settings.api_version,
        "docs": "/docs"
    }

