"""
得意先マスタモデル

得意先マスタテーブル（cm_custom_mst）のSQLModelモデル定義
"""
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class KoujyouMaster(SQLModel, table=True):
    """
    得意先マスタテーブルモデル
    
    テーブル名: cm_custom_mst
    """
    __tablename__ = "m_koujyou"
    
    # 主キー（複合キー）
    previous_factory_code: str = Field(max_length=4, primary_key=True, description="従来工場コード")
    company_code: str = Field(max_length=4, primary_key=True, description="会社コード")
    product_factory_code: str = Field(max_length=4, primary_key=True, description="商品工場コード")
    start_operation_date: date = Field(primary_key=True, description="運用開始日")
    end_operation_date: date = Field(primary_key=True, description="運用終了日")
    
    # 基本情報
    previous_factory_name: Optional[str] = Field(default=None, max_length=100, description="従来工場名")
    product_factory_name: Optional[str] = Field(default=None, max_length=100, description="商品工場名")
    material_department_code: Optional[str] = Field(default=None, max_length=4, description="マテリアル部署コード")
    environmental_information: Optional[str] = Field(default=None, max_length=100, description="環境情報")
    authentication_flag: Optional[str] = Field(default=None, max_length=100, description="認証フラグ")
    group_corporate_code: Optional[str] = Field(default=None, max_length=4, description="企業コード")
    integration_pattern: Optional[str] = Field(default=None, max_length=100, description="連携パターン")
    hulftid: Optional[str] = Field(default=None, max_length=100, description="HULFTID")
    
    # 旧コード情報
    
    # 国際化情報
    
    # 登録情報
    
    # 更新情報

