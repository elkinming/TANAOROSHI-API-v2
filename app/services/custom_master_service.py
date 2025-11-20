"""
得意先マスタサービス

得意先マスタに関するビジネスロジック処理
"""
from datetime import date
from typing import Optional, List
from sqlmodel import Session
from fastapi import HTTPException, status
from app.repositories.custom_master_repository import CustomMasterRepository
from app.schemas.custom_master import (
    CustomMasterCreate,
    CustomMasterUpdate,
    CustomMasterResponse
)
from app.constants.error_codes import ErrorCode, ErrorMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CustomMasterService:
    """得意先マスタサービスクラス"""
    
    def __init__(self, session: Session):
        """
        サービスを初期化する
        
        Args:
            session: データベースセッション
        """
        self.repository = CustomMasterRepository(session)
    
    def create_custom_master(
        self,
        custom_master_data: CustomMasterCreate
    ) -> CustomMasterResponse:
        """
        得意先マスタを作成する
        
        Args:
            custom_master_data: 作成する得意先マスタデータ
            
        Returns:
            CustomMasterResponse: 作成された得意先マスタ
            
        Raises:
            HTTPException: 既に存在する場合
        """
        logger.info(
            f"得意先マスタ作成開始: corporate_cd={custom_master_data.corporate_cd}, "
            f"toku_cd={custom_master_data.toku_cd}, "
            f"ty_date_from={custom_master_data.ty_date_from}"
        )
        
        # 既存データの確認
        existing = self.repository.get_by_id(
            custom_master_data.corporate_cd,
            custom_master_data.toku_cd,
            custom_master_data.ty_date_from
        )
        
        if existing:
            logger.warning(
                f"得意先マスタが既に存在: corporate_cd={custom_master_data.corporate_cd}, "
                f"toku_cd={custom_master_data.toku_cd}, "
                f"ty_date_from={custom_master_data.ty_date_from}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_ALREADY_EXISTS)
            )
        
        try:
            db_item = self.repository.create(custom_master_data)
            logger.info(f"得意先マスタ作成成功: ID={db_item.corporate_cd}-{db_item.toku_cd}-{db_item.ty_date_from}")
            return CustomMasterResponse.model_validate(db_item)
        except Exception as e:
            logger.error(f"得意先マスタ作成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_CREATE_FAILED, str(e))
            )
    
    def get_custom_master(
        self,
        corporate_cd: str,
        toku_cd: str,
        ty_date_from: date
    ) -> CustomMasterResponse:
        """
        得意先マスタを取得する
        
        Args:
            corporate_cd: 法人コード
            toku_cd: 得意先コード
            ty_date_from: 適用開始日
            
        Returns:
            CustomMasterResponse: 得意先マスタ
            
        Raises:
            HTTPException: 見つからない場合
        """
        logger.debug(
            f"得意先マスタ取得: corporate_cd={corporate_cd}, "
            f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
        )
        
        db_item = self.repository.get_by_id(corporate_cd, toku_cd, ty_date_from)
        
        if not db_item:
            logger.warning(
                f"得意先マスタが見つかりません: corporate_cd={corporate_cd}, "
                f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_NOT_FOUND)
            )
        
        return CustomMasterResponse.model_validate(db_item)
    
    def get_custom_masters(
        self,
        skip: int = 0,
        limit: int = 100,
        corporate_cd: Optional[str] = None,
        toku_cd: Optional[str] = None,
        toku_name: Optional[str] = None
    ) -> List[CustomMasterResponse]:
        """
        得意先マスタのリストを取得する
        
        Args:
            skip: スキップする件数
            limit: 取得する最大件数
            corporate_cd: 法人コードでフィルタ（オプション）
            toku_cd: 得意先コードでフィルタ（オプション）
            toku_name: 得意先名称で曖昧検索（オプション）
            
        Returns:
            List[CustomMasterResponse]: 得意先マスタのリスト
        """
        logger.debug(
            f"得意先マスタリスト取得: skip={skip}, limit={limit}, "
            f"corporate_cd={corporate_cd}, toku_cd={toku_cd}, toku_name={toku_name}"
        )
        
        db_items = self.repository.get_all(
            skip=skip,
            limit=limit,
            corporate_cd=corporate_cd,
            toku_cd=toku_cd,
            toku_name=toku_name
        )
        
        return [CustomMasterResponse.model_validate(item) for item in db_items]
    
    def update_custom_master(
        self,
        corporate_cd: str,
        toku_cd: str,
        ty_date_from: date,
        custom_master_data: CustomMasterUpdate
    ) -> CustomMasterResponse:
        """
        得意先マスタを更新する
        
        Args:
            corporate_cd: 法人コード
            toku_cd: 得意先コード
            ty_date_from: 適用開始日
            custom_master_data: 更新するデータ
            
        Returns:
            CustomMasterResponse: 更新された得意先マスタ
            
        Raises:
            HTTPException: 見つからない場合
        """
        logger.info(
            f"得意先マスタ更新開始: corporate_cd={corporate_cd}, "
            f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
        )
        
        db_item = self.repository.update(
            corporate_cd,
            toku_cd,
            ty_date_from,
            custom_master_data
        )
        
        if not db_item:
            logger.warning(
                f"得意先マスタが見つかりません（更新）: corporate_cd={corporate_cd}, "
                f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_NOT_FOUND)
            )
        
        logger.info(f"得意先マスタ更新成功: ID={corporate_cd}-{toku_cd}-{ty_date_from}")
        return CustomMasterResponse.model_validate(db_item)
    
    def delete_custom_master(
        self,
        corporate_cd: str,
        toku_cd: str,
        ty_date_from: date
    ) -> None:
        """
        得意先マスタを削除する
        
        Args:
            corporate_cd: 法人コード
            toku_cd: 得意先コード
            ty_date_from: 適用開始日
            
        Raises:
            HTTPException: 見つからない場合
        """
        logger.info(
            f"得意先マスタ削除開始: corporate_cd={corporate_cd}, "
            f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
        )
        
        success = self.repository.delete(corporate_cd, toku_cd, ty_date_from)
        
        if not success:
            logger.warning(
                f"得意先マスタが見つかりません（削除）: corporate_cd={corporate_cd}, "
                f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_NOT_FOUND)
            )
        
        logger.info(f"得意先マスタ削除成功: ID={corporate_cd}-{toku_cd}-{ty_date_from}")

