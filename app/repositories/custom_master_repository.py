"""
得意先マスタリポジトリ

得意先マスタテーブルへのデータアクセス処理
"""
from datetime import date
from typing import Optional, List
from sqlmodel import Session, select
from app.models.custom_master import CustomMaster
from app.schemas.custom_master import CustomMasterCreate, CustomMasterUpdate


class CustomMasterRepository:
    """得意先マスタリポジトリクラス"""
    
    def __init__(self, session: Session):
        """
        リポジトリを初期化する
        
        Args:
            session: データベースセッション
        """
        self.session = session
    
    def create(self, custom_master_data: CustomMasterCreate) -> CustomMaster:
        """
        得意先マスタを作成する
        
        Args:
            custom_master_data: 作成する得意先マスタデータ
            
        Returns:
            CustomMaster: 作成された得意先マスタ
        """
        db_item = CustomMaster(**custom_master_data.model_dump())
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item
    
    def get_by_id(
        self,
        corporate_cd: str,
        toku_cd: str,
        ty_date_from: date
    ) -> Optional[CustomMaster]:
        """
        主キーで得意先マスタを取得する
        
        Args:
            corporate_cd: 法人コード
            toku_cd: 得意先コード
            ty_date_from: 適用開始日
            
        Returns:
            Optional[CustomMaster]: 得意先マスタ（見つからない場合はNone）
        """
        statement = select(CustomMaster).where(
            CustomMaster.corporate_cd == corporate_cd,
            CustomMaster.toku_cd == toku_cd,
            CustomMaster.ty_date_from == ty_date_from
        )
        return self.session.exec(statement).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        corporate_cd: Optional[str] = None,
        toku_cd: Optional[str] = None,
        toku_name: Optional[str] = None
    ) -> List[CustomMaster]:
        """
        得意先マスタのリストを取得する
        
        Args:
            skip: スキップする件数
            limit: 取得する最大件数
            corporate_cd: 法人コードでフィルタ（オプション）
            toku_cd: 得意先コードでフィルタ（オプション）
            toku_name: 得意先名称で曖昧検索（オプション）
            
        Returns:
            List[CustomMaster]: 得意先マスタのリスト
        """
        statement = select(CustomMaster)
        
        # フィルタ条件を追加
        if corporate_cd:
            statement = statement.where(CustomMaster.corporate_cd == corporate_cd)
        if toku_cd:
            statement = statement.where(CustomMaster.toku_cd == toku_cd)
        if toku_name:
            # 曖昧検索（大文字小文字を区別しない）
            statement = statement.where(CustomMaster.toku_name.ilike(f"%{toku_name}%"))
        
        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def update(
        self,
        corporate_cd: str,
        toku_cd: str,
        ty_date_from: date,
        custom_master_data: CustomMasterUpdate
    ) -> Optional[CustomMaster]:
        """
        得意先マスタを更新する
        
        Args:
            corporate_cd: 法人コード
            toku_cd: 得意先コード
            ty_date_from: 適用開始日
            custom_master_data: 更新するデータ
            
        Returns:
            Optional[CustomMaster]: 更新された得意先マスタ（見つからない場合はNone）
        """
        db_item = self.get_by_id(corporate_cd, toku_cd, ty_date_from)
        if not db_item:
            return None
        
        # 更新データを適用
        update_data = custom_master_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        # 更新日時を自動設定
        from datetime import datetime
        db_item.upd_dtime = datetime.now()
        
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item
    
    def delete(
        self,
        corporate_cd: str,
        toku_cd: str,
        ty_date_from: date
    ) -> bool:
        """
        得意先マスタを削除する
        
        Args:
            corporate_cd: 法人コード
            toku_cd: 得意先コード
            ty_date_from: 適用開始日
            
        Returns:
            bool: 削除成功時はTrue、見つからない場合はFalse
        """
        db_item = self.get_by_id(corporate_cd, toku_cd, ty_date_from)
        if not db_item:
            return False
        
        self.session.delete(db_item)
        self.session.commit()
        return True

