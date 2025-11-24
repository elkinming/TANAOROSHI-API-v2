"""
工場マスタサービス

工場マスタに関するビジネスロジック処理
"""
from datetime import date
from typing import Optional, List, Dict, Any
from sqlmodel import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
from app.repositories.custom_master_repository import CustomMasterRepository
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.koujyou_master import KoujyouMasterBase, KoujyouMasterResponse
from app.schemas.custom_master import (
    CustomMasterCreate,
    CustomMasterUpdate,
    CustomMasterResponse
)
from app.constants.error_codes import ErrorCode, ErrorMessage
from app.utils.logger import get_logger


logger = get_logger(__name__)


class InventoryService:
    """工場マスタサービスクラス"""

    def __init__(self, session: Session):
        """
        サービスを初期化する

        Args:
            session: データベースセッション
        """
        self.repository = InventoryRepository(session)


    def get_koujyou_master_all(
        self,
        previous_factory_code: Optional[str] = None,
        product_factory_code: Optional[str] = None,
        search_keyword: Optional[str] = None
    ) -> List[KoujyouMasterResponse]:
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
            f"工場マスタリスト取得: previous_factory_code={previous_factory_code}, "
            f"product_factory_code={product_factory_code}, search_keyword={search_keyword}"
        )

        db_items = self.repository.get_all(
            previous_factory_code=previous_factory_code,
            product_factory_code=product_factory_code,
            search_keyword=search_keyword
        )

        return [KoujyouMasterResponse.model_validate(item) for item in db_items]


    def create_koujyou_master(
        self,
        koujyou_master_data: KoujyouMasterBase
    ) -> KoujyouMasterResponse:
        """
        工場マスタを作成する

        Args:
            koujyou_master_data: 作成する工場マスタデータ

        Returns:
            KoujyouMasterResponse: 作成された工場マスタ

        Raises:
            HTTPException: 既に存在する場合、または作成エラーの場合
        """
        logger.info(
            f"工場マスタ作成開始: {koujyou_master_data}"
        )

        # 既存データの確認（例えばuniqueなキーなどで重複チェック。リポジトリに追加項目が必要ならここで確認）
        exists = self.repository.get_by_unique_keys(koujyou_master_data)
        if exists:
            logger.warning("工場マスタが既に存在します")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="既に工場マスタが存在します"
            )

        try:
            db_item = self.repository.create_koujyou_master(koujyou_master_data)
            logger.info(f"工場マスタ作成成功: {db_item}")
            return KoujyouMasterResponse.model_validate(db_item)
        except Exception as e:
            logger.error(f"工場マスタ作成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="工場マスタの作成中にエラーが発生しました"
            )

    def update_koujyou_master(
        self,
        koujyou_master_data: KoujyouMasterBase
    ) -> KoujyouMasterResponse:
        """
        工場マスタを更新する

        Args:
            koujyou_master_data: 更新する工場マスタデータ

        Returns:
            KoujyouMasterResponse: 更新された工場マスタ

        Raises:
            HTTPException: 見つからない場合、または更新エラーの場合
        """
        logger.info(
            f"工場マスタ更新開始: {koujyou_master_data}"
        )

        try:
            db_item = self.repository.update_koujyou_master(koujyou_master_data)
            if not db_item:
                logger.warning("工場マスタが見つかりません（更新）")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="工場マスタが見つかりません"
                )
            logger.info(f"工場マスタ更新成功: {db_item}")
            return KoujyouMasterResponse.model_validate(db_item)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"工場マスタ更新エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="工場マスタの更新中にエラーが発生しました"
            )

    def create_koujyou_master_batch(
        self,
        koujyou_master_data_list: List[KoujyouMasterBase]
    ) -> List[KoujyouMasterResponse]:
        """
        工場マスタを一括作成する

        Args:
            koujyou_master_data_list: 作成する工場マスタデータのリスト

        Returns:
            List[KoujyouMasterResponse]: 作成された工場マスタのリスト

        Raises:
            HTTPException: 作成エラーの場合
        """
        logger.info(
            f"工場マスタ一括作成開始: {len(koujyou_master_data_list)}件"
        )

        try:
            db_items = self.repository.create_koujyou_master_batch(koujyou_master_data_list)
            logger.info(f"工場マスタ一括作成成功: {len(db_items)}件")
            return [KoujyouMasterResponse.model_validate(item) for item in db_items]

        except (IntegrityError, DataError) as e:
            # データベースの制約違反やデータエラーは400 Bad Request
            logger.warning(f"工場マスタ一括作成データエラー: {e}")
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"データが無効です"
                # detail=f"データが無効です: {error_message}"
            )

        except DatabaseError as e:
            # その他のデータベースエラーは500 Internal Server Error
            logger.error(f"工場マスタ一括作成データベースエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
            )

        except Exception as e:
            # 予期しないエラーは500 Internal Server Error
            logger.error(f"工場マスタ一括作成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="工場マスタの一括作成中にエラーが発生しました"
            )

    def update_koujyou_master_batch(
        self,
        koujyou_master_data_list: List[KoujyouMasterBase]
    ) -> Dict[str, Any]:
        """
        工場マスタを一括更新する

        Args:
            koujyou_master_data_list: 更新する工場マスタデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[KoujyouMasterResponse] - 更新された工場マスタのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        logger.info(
            f"工場マスタ一括更新開始: {len(koujyou_master_data_list)}件"
        )

        try:
            result = self.repository.update_koujyou_master_batch(koujyou_master_data_list)
            ok_records = result["ok_records"]
            error_records = result["error_records"]

            logger.info(
                f"工場マスタ一括更新完了: 成功{len(ok_records)}件, エラー{len(error_records)}件"
            )

            return {
                "ok_records": [KoujyouMasterResponse.model_validate(item) for item in ok_records],
                "error_records": error_records
            }

        except (IntegrityError, DataError) as e:
            # データベースの制約違反やデータエラーは400 Bad Request
            logger.warning(f"工場マスタ一括更新データエラー: {e}")
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"データが無効です"
            )

        except DatabaseError as e:
            # その他のデータベースエラーは500 Internal Server Error
            logger.error(f"工場マスタ一括更新データベースエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
            )

        except Exception as e:
            # 予期しないエラーは500 Internal Server Error
            logger.error(f"工場マスタ一括更新エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="工場マスタの一括更新中にエラーが発生しました"
            )

    def create_multiple_koujyou_master(
        self,
        koujyou_master_data_list: List[KoujyouMasterBase]
    ) -> Dict[str, Any]:
        """
        工場マスタを一括作成する

        Args:
            koujyou_master_data_list: 作成する工場マスタデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[KoujyouMasterResponse] - 作成された工場マスタのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        logger.info(
            f"工場マスタ一括作成開始: {len(koujyou_master_data_list)}件"
        )

        try:
            result = self.repository.create_multiple_koujyou_master(koujyou_master_data_list)
            ok_records = result["ok_records"]
            error_records = result["error_records"]

            logger.info(
                f"工場マスタ一括作成完了: 成功{len(ok_records)}件, エラー{len(error_records)}件"
            )

            return {
                "ok_records": [KoujyouMasterResponse.model_validate(item) for item in ok_records],
                "error_records": error_records
            }

        except (IntegrityError, DataError) as e:
            # データベースの制約違反やデータエラーは400 Bad Request
            logger.warning(f"工場マスタ一括作成データエラー: {e}")
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"データが無効です"
            )

        except DatabaseError as e:
            # その他のデータベースエラーは500 Internal Server Error
            logger.error(f"工場マスタ一括作成データベースエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
            )

        except Exception as e:
            # 予期しないエラーは500 Internal Server Error
            logger.error(f"工場マスタ一括作成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="工場マスタの一括作成中にエラーが発生しました"
            )

    def delete_multiple_koujyou_master(
        self,
        koujyou_master_data_list: List[KoujyouMasterBase]
    ) -> Dict[str, Any]:
        """
        工場マスタを一括削除する

        Args:
            koujyou_master_data_list: 削除する工場マスタデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[KoujyouMasterResponse] - 削除された工場マスタのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        logger.info(
            f"工場マスタ一括削除開始: {len(koujyou_master_data_list)}件"
        )

        try:
            result = self.repository.delete_multiple_koujyou_master(koujyou_master_data_list)
            ok_records = result["ok_records"]
            error_records = result["error_records"]

            logger.info(
                f"工場マスタ一括削除完了: 成功{len(ok_records)}件, エラー{len(error_records)}件"
            )

            return {
                "ok_records": [KoujyouMasterResponse.model_validate(item) for item in ok_records],
                "error_records": error_records
            }

        except (IntegrityError, DataError) as e:
            # データベースの制約違反やデータエラーは400 Bad Request
            logger.warning(f"工場マスタ一括削除データエラー: {e}")
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"データが無効です"
            )

        except DatabaseError as e:
            # その他のデータベースエラーは500 Internal Server Error
            logger.error(f"工場マスタ一括削除データベースエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
            )

        except Exception as e:
            # 予期しないエラーは500 Internal Server Error
            logger.error(f"工場マスタ一括削除エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="工場マスタの一括削除中にエラーが発生しました"
            )



    # def create_custom_master(
    #     self,
    #     custom_master_data: CustomMasterCreate
    # ) -> CustomMasterResponse:
    #     """
    #     得意先マスタを作成する

    #     Args:
    #         custom_master_data: 作成する得意先マスタデータ

    #     Returns:
    #         CustomMasterResponse: 作成された得意先マスタ

    #     Raises:
    #         HTTPException: 既に存在する場合
    #     """
    #     logger.info(
    #         f"得意先マスタ作成開始: corporate_cd={custom_master_data.corporate_cd}, "
    #         f"toku_cd={custom_master_data.toku_cd}, "
    #         f"ty_date_from={custom_master_data.ty_date_from}"
    #     )

    #     # 既存データの確認
    #     existing = self.repository.get_by_id(
    #         custom_master_data.corporate_cd,
    #         custom_master_data.toku_cd,
    #         custom_master_data.ty_date_from
    #     )

    #     if existing:
    #         logger.warning(
    #             f"得意先マスタが既に存在: corporate_cd={custom_master_data.corporate_cd}, "
    #             f"toku_cd={custom_master_data.toku_cd}, "
    #             f"ty_date_from={custom_master_data.ty_date_from}"
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_ALREADY_EXISTS)
    #         )

    #     try:
    #         db_item = self.repository.create(custom_master_data)
    #         logger.info(f"得意先マスタ作成成功: ID={db_item.corporate_cd}-{db_item.toku_cd}-{db_item.ty_date_from}")
    #         return CustomMasterResponse.model_validate(db_item)
    #     except Exception as e:
    #         logger.error(f"得意先マスタ作成エラー: {e}")
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_CREATE_FAILED, str(e))
    #         )

    # def get_custom_master(
    #     self,
    #     corporate_cd: str,
    #     toku_cd: str,
    #     ty_date_from: date
    # ) -> CustomMasterResponse:
    #     """
    #     得意先マスタを取得する

    #     Args:
    #         corporate_cd: 法人コード
    #         toku_cd: 得意先コード
    #         ty_date_from: 適用開始日

    #     Returns:
    #         CustomMasterResponse: 得意先マスタ

    #     Raises:
    #         HTTPException: 見つからない場合
    #     """
    #     logger.debug(
    #         f"得意先マスタ取得: corporate_cd={corporate_cd}, "
    #         f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
    #     )

    #     db_item = self.repository.get_by_id(corporate_cd, toku_cd, ty_date_from)

    #     if not db_item:
    #         logger.warning(
    #             f"得意先マスタが見つかりません: corporate_cd={corporate_cd}, "
    #             f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_NOT_FOUND)
    #         )

    #     return CustomMasterResponse.model_validate(db_item)

    # def update_custom_master(
    #     self,
    #     corporate_cd: str,
    #     toku_cd: str,
    #     ty_date_from: date,
    #     custom_master_data: CustomMasterUpdate
    # ) -> CustomMasterResponse:
    #     """
    #     得意先マスタを更新する

    #     Args:
    #         corporate_cd: 法人コード
    #         toku_cd: 得意先コード
    #         ty_date_from: 適用開始日
    #         custom_master_data: 更新するデータ

    #     Returns:
    #         CustomMasterResponse: 更新された得意先マスタ

    #     Raises:
    #         HTTPException: 見つからない場合
    #     """
    #     logger.info(
    #         f"得意先マスタ更新開始: corporate_cd={corporate_cd}, "
    #         f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
    #     )

    #     db_item = self.repository.update(
    #         corporate_cd,
    #         toku_cd,
    #         ty_date_from,
    #         custom_master_data
    #     )

    #     if not db_item:
    #         logger.warning(
    #             f"得意先マスタが見つかりません（更新）: corporate_cd={corporate_cd}, "
    #             f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_NOT_FOUND)
    #         )

    #     logger.info(f"得意先マスタ更新成功: ID={corporate_cd}-{toku_cd}-{ty_date_from}")
    #     return CustomMasterResponse.model_validate(db_item)

    # def delete_custom_master(
    #     self,
    #     corporate_cd: str,
    #     toku_cd: str,
    #     ty_date_from: date
    # ) -> None:
    #     """
    #     得意先マスタを削除する

    #     Args:
    #         corporate_cd: 法人コード
    #         toku_cd: 得意先コード
    #         ty_date_from: 適用開始日

    #     Raises:
    #         HTTPException: 見つからない場合
    #     """
    #     logger.info(
    #         f"得意先マスタ削除開始: corporate_cd={corporate_cd}, "
    #         f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
    #     )

    #     success = self.repository.delete(corporate_cd, toku_cd, ty_date_from)

    #     if not success:
    #         logger.warning(
    #             f"得意先マスタが見つかりません（削除）: corporate_cd={corporate_cd}, "
    #             f"toku_cd={toku_cd}, ty_date_from={ty_date_from}"
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=ErrorMessage.get_message(ErrorCode.CUSTOM_MASTER_NOT_FOUND)
    #         )

    #     logger.info(f"得意先マスタ削除成功: ID={corporate_cd}-{toku_cd}-{ty_date_from}")

