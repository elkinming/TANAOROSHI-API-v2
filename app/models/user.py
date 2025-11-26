"""
ユーザーモデル

ユーザーテーブルのSQLModelモデル定義
"""
from typing import Optional
import uuid
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    ユーザーテーブルモデル

    テーブル名: users
    """
    __tablename__ = "m_user"

    # 主キー
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="ユーザーID"
    )

    # 基本情報
    name: Optional[str] = Field(default=None, description="名前")
    lastname: Optional[str] = Field(default=None, description="姓")
    age: Optional[int] = Field(default=None, description="年齢")
    country: Optional[str] = Field(default=None, description="国")
    home_address: Optional[str] = Field(default=None, description="住所")

