"""
ユーザースキーマ

ユーザーのAPIリクエスト/レスポンススキーマ定義
"""
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """ユーザーの基本スキーマ"""
    id: Optional[str] = Field(default=None, description="ユーザーID")
    name: Optional[str] = Field(default=None, description="名前")
    lastname: Optional[str] = Field(default=None, description="姓")
    age: Optional[int] = Field(default=None, description="年齢")
    country: Optional[str] = Field(default=None, description="国")
    home_address: Optional[str] = Field(default=None, description="住所")


class UserResponse(UserBase):
    """ユーザーレスポンススキーマ"""
    model_config = {"from_attributes": True}

