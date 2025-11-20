"""
データベース接続設定

SQLModelを使用したデータベース接続の設定と管理
"""
from sqlmodel import create_engine, Session
from typing import Generator
from app.config import settings


# データベースエンジンの作成
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,  # True: SQLクエリをログに出力（開発時）、False: 出力しない（本番環境）
    pool_pre_ping=settings.database_pool_pre_ping,  # 接続の有効性を確認
    pool_size=settings.database_pool_size,  # 接続プールサイズ
    max_overflow=settings.database_max_overflow  # 最大オーバーフロー
)


def get_session() -> Generator[Session, None, None]:
    """
    データベースセッションを取得する
    
    Yields:
        Session: SQLModelセッション
    """
    with Session(engine) as session:
        yield session

