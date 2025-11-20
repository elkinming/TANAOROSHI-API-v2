"""
得意先マスタモデル

得意先マスタテーブル（cm_custom_mst）のSQLModelモデル定義
"""
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class CustomMaster(SQLModel, table=True):
    """
    得意先マスタテーブルモデル
    
    テーブル名: cm_custom_mst
    """
    __tablename__ = "cm_custom_mst"
    
    # 主キー（複合キー）
    corporate_cd: str = Field(max_length=7, primary_key=True, description="法人コード")
    toku_cd: str = Field(max_length=4, primary_key=True, description="得意先コード")
    ty_date_from: date = Field(primary_key=True, description="適用開始日")
    
    # 基本情報
    ty_date_to: Optional[date] = Field(default=None, description="適用終了日")
    toku_name: str = Field(max_length=40, description="得意先名")
    toku_abbr: Optional[str] = Field(default=None, max_length=20, description="得意先略称")
    
    # 旧コード情報
    old_toku_cd1: Optional[str] = Field(default=None, max_length=4, description="旧得意先コード1")
    old_toku_cd2: Optional[str] = Field(default=None, max_length=4, description="旧得意先コード2")
    old_toku_cd3: Optional[str] = Field(default=None, max_length=4, description="旧得意先コード3")
    
    # 国際化情報
    country_cd: str = Field(default="JP", max_length=2, description="国コード")
    currency_cd: str = Field(default="JPY", max_length=3, description="通貨コード")
    
    # 登録情報
    crt_corporate_cd: str = Field(max_length=7, description="登録者法人コード")
    crt_user_id: str = Field(max_length=20, description="登録者ID")
    crt_dtime: datetime = Field(default_factory=datetime.now, description="登録日時")
    crt_pg: str = Field(max_length=20, description="登録PG")
    
    # 更新情報
    upd_corporate_cd: str = Field(max_length=7, description="更新者法人コード")
    upd_user_id: str = Field(max_length=20, description="更新者ID")
    upd_dtime: datetime = Field(default_factory=datetime.now, description="更新日時")
    upd_pg: str = Field(max_length=20, description="更新PG")

