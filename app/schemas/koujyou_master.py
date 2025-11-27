"""
得意先マスタスキーマ

得意先マスタのAPIリクエスト/レスポンススキーマ定義
"""
from datetime import date, datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class KoujyouMasterBase(BaseModel):
    """得意先マスタの基本スキーマ"""
    company_code: str = Field(max_length=100, description="会社コード")
    previous_factory_code: str = Field(max_length=100, description="従来工場コード")
    product_factory_code: str = Field(max_length=100, description="商品工場コード")
    start_operation_date: date = Field(description="運用開始日")
    end_operation_date: date = Field(description="運用終了日")
    previous_factory_name: Optional[str] = Field(default=None, max_length=100, description="従来工場名")
    product_factory_name: Optional[str] = Field(default=None, max_length=100, description="商品工場名")
    material_department_code: Optional[str] = Field(default=None, max_length=100, description="マテリアル部署コード")
    environmental_information: Optional[str] = Field(default=None, max_length=100, description="環境情報")
    authentication_flag: Optional[str] = Field(default=None, max_length=100, description="認証フラグ")
    group_corporate_code: Optional[str] = Field(default=None, max_length=100, description="企業コード")
    integration_pattern: Optional[str] = Field(default=None, max_length=100, description="連携パターン")
    hulftid: Optional[str] = Field(default=None, max_length=100, description="HULFTID")


class KoujyouMasterResponse(KoujyouMasterBase):
    """得意先マスタレスポンススキーマ"""
    model_config = {"from_attributes": True}


class CommitRecordErrorBase(BaseModel, Generic[T]):
    """コミットエラーレコードスキーマ"""
    record: Optional[T] = Field(default=None, description="エラーが発生したレコード")
    level: str = Field(default="", description="エラーレベル")
    message: str = Field(default="", description="エラーメッセージ")
    detail: str = Field(default="", description="エラー詳細")
    code: str = Field(default="", description="エラーコード")


class CommitRecordErrorResponse(CommitRecordErrorBase):
    """得意先マスタレスポンススキーマ"""
    model_config = {"from_attributes": True}


class CheckIntegrityRequest(BaseModel):
    """整合性チェックリクエストスキーマ"""
    record: KoujyouMasterBase = Field(..., description="チェック対象のレコード")


class CheckIntegrityResponse(BaseModel):
    """整合性チェックレスポンススキーマ"""
    error_codes: list[str] = Field(default_factory=list, description="エラーコードリスト")
    error_messages: list[str] = Field(default_factory=list, description="エラーメッセージリスト")
