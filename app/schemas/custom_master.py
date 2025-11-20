"""
得意先マスタスキーマ

得意先マスタのAPIリクエスト/レスポンススキーマ定義
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class CustomMasterBase(BaseModel):
    """得意先マスタの基本スキーマ"""
    corporate_cd: str = Field(..., max_length=7, description="法人コード")
    toku_cd: str = Field(..., max_length=4, description="得意先コード")
    ty_date_from: date = Field(..., description="適用開始日")
    ty_date_to: Optional[date] = Field(None, description="適用終了日")
    toku_name: str = Field(..., max_length=40, description="得意先名")
    toku_abbr: Optional[str] = Field(None, max_length=20, description="得意先略称")
    old_toku_cd1: Optional[str] = Field(None, max_length=4, description="旧得意先コード1")
    old_toku_cd2: Optional[str] = Field(None, max_length=4, description="旧得意先コード2")
    old_toku_cd3: Optional[str] = Field(None, max_length=4, description="旧得意先コード3")
    country_cd: str = Field(default="JP", max_length=2, description="国コード")
    currency_cd: str = Field(default="JPY", max_length=3, description="通貨コード")


class CustomMasterCreate(CustomMasterBase):
    """得意先マスタ作成スキーマ"""
    crt_corporate_cd: str = Field(..., max_length=7, description="登録者法人コード")
    crt_user_id: str = Field(..., max_length=20, description="登録者ID")
    crt_pg: str = Field(..., max_length=20, description="登録PG")
    upd_corporate_cd: str = Field(..., max_length=7, description="更新者法人コード")
    upd_user_id: str = Field(..., max_length=20, description="更新者ID")
    upd_pg: str = Field(..., max_length=20, description="更新PG")


class CustomMasterUpdate(BaseModel):
    """得意先マスタ更新スキーマ"""
    ty_date_to: Optional[date] = Field(None, description="適用終了日")
    toku_name: Optional[str] = Field(None, max_length=40, description="得意先名")
    toku_abbr: Optional[str] = Field(None, max_length=20, description="得意先略称")
    old_toku_cd1: Optional[str] = Field(None, max_length=4, description="旧得意先コード1")
    old_toku_cd2: Optional[str] = Field(None, max_length=4, description="旧得意先コード2")
    old_toku_cd3: Optional[str] = Field(None, max_length=4, description="旧得意先コード3")
    country_cd: Optional[str] = Field(None, max_length=2, description="国コード")
    currency_cd: Optional[str] = Field(None, max_length=3, description="通貨コード")
    upd_corporate_cd: str = Field(..., max_length=7, description="更新者法人コード")
    upd_user_id: str = Field(..., max_length=20, description="更新者ID")
    upd_pg: str = Field(..., max_length=20, description="更新PG")


class CustomMasterResponse(CustomMasterBase):
    """得意先マスタレスポンススキーマ"""
    crt_corporate_cd: str = Field(..., description="登録者法人コード")
    crt_user_id: str = Field(..., description="登録者ID")
    crt_dtime: datetime = Field(..., description="登録日時")
    crt_pg: str = Field(..., description="登録PG")
    upd_corporate_cd: str = Field(..., description="更新者法人コード")
    upd_user_id: str = Field(..., description="更新者ID")
    upd_dtime: datetime = Field(..., description="更新日時")
    upd_pg: str = Field(..., description="更新PG")
    
    model_config = {"from_attributes": True}

