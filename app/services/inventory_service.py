"""
工場マスタサービス

工場マスタに関するビジネスロジック処理
"""
from datetime import date
from typing import Optional, List, Dict, Any, get_type_hints, Union
from sqlmodel import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
from app.repositories.custom_master_repository import CustomMasterRepository
from app.repositories.inventory_repository import InventoryRepository
from app.models.koujyou_master import KoujyouMaster
from app.schemas.koujyou_master import (
    KoujyouMasterBase,
    KoujyouMasterResponse,
    CheckIntegrityResponse
)
from app.schemas.custom_master import (
    CustomMasterCreate,
    CustomMasterUpdate,
    CustomMasterResponse
)
from app.constants.error_codes import ErrorCode, ErrorMessage
from app.utils.logger import get_logger


logger = get_logger(__name__)


def _format_pk_details(record: Union[KoujyouMasterBase, KoujyouMaster]) -> str:
    """
    プライマリキー詳細をフォーマットする

    Args:
        record: レコードオブジェクト（KoujyouMasterBaseまたはKoujyouMaster）

    Returns:
        str: フォーマットされたプライマリキー詳細文字列
    """
    return f"{record.company_code} / {record.previous_factory_code} / {record.product_factory_code} / {record.start_operation_date} / {record.end_operation_date}"


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

    def check_integrity(
        self,
        koujyou_master_data: KoujyouMasterBase,
        pk_check: bool,
        datatype_check: bool,
        time_logic_check: bool,


    ) -> CheckIntegrityResponse:
        """
        レコードの整合性をチェックする

        Args:
            koujyou_master_data: チェック対象のレコード
            pk_check: プライマリキーチェック
            datatype_check: データタイプチェック
            time_logic_check: 時間ロジックチェック

        Returns:
            CheckIntegrityResponse: 整合性チェック結果
        """
        logger.info(
            f"整合性チェック開始: record={koujyou_master_data}, "
            f"pk_check={pk_check}, datatype_check={datatype_check}, time_logic_check={time_logic_check}"
        )

        try:
            print(f"record: {koujyou_master_data}")
            print(f"pk_check: {pk_check}")
            print(f"datatype_check: {datatype_check}")
            print(f"time_logic_check: {time_logic_check}")

            pk_detail = _format_pk_details(koujyou_master_data)
            response = CheckIntegrityResponse(
                error_codes=[],
                error_messages=[],
                pk_detail=pk_detail,
                error_data=[]
            )

            if pk_check:
                existing = self.repository.get_by_unique_keys(koujyou_master_data)
                if existing:
                    response.error_codes.append("PK_CHECK_FAILED")
                    response.error_messages.append("プライマリキーが存在しません")
                    response.error_data.append({})

            if datatype_check:
                self._validate_datatypes(koujyou_master_data, response)

            if time_logic_check:
                self._validate_time_logic(koujyou_master_data, response)



            return response

        except Exception as e:
            logger.error(f"整合性チェックエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="整合性チェック中にエラーが発生しました"
            )

    def _validate_datatypes(
        self,
        koujyou_master_data: KoujyouMasterBase,
        response: CheckIntegrityResponse
    ) -> None:
        """
        データタイプを検証する

        Args:
            koujyou_master_data: 検証対象のレコード
            response: エラーレスポンスオブジェクト（エラーを追加する）
        """
        # モデルのフィールド定義を取得
        model_fields = KoujyouMaster.model_fields
        model_type_hints = get_type_hints(KoujyouMaster, include_extras=True)

        # データのフィールドを取得
        data_dict = koujyou_master_data.model_dump()

        for field_name, field_info in model_fields.items():
            # データにフィールドが存在するか確認
            if field_name not in data_dict:
                continue

            value = data_dict[field_name]
            expected_type = model_type_hints.get(field_name)

            # max_lengthを取得（metadataから）
            max_length = None
            if hasattr(field_info, 'metadata') and field_info.metadata:
                for meta in field_info.metadata:
                    # metadataにはMaxLenオブジェクトが含まれる
                    if hasattr(meta, 'max_length'):
                        max_length = meta.max_length
                        break

            # None値の処理（Optionalフィールドの場合）
            if value is None:
                # Optional型の場合はNoneが許可されている
                if expected_type:
                    type_str = str(expected_type)
                    # Optional[Type] や Union[Type, None] の場合はNoneが許可されている
                    if 'None' in type_str:
                        continue  # Noneは許可されている
                    else:
                        # Noneが許可されていない型でNoneが来た場合
                        response.error_codes.append("DATATYPE_CHECK_FAILED")
                        response.error_messages.append(
                            f"フィールド '{field_name}' はNoneを許可していませんが、Noneが設定されています"
                        )
                        error_dict = {
                            "field_name": field_name,
                            "max_length": None,
                            "expected_type_str": str(expected_type) if expected_type else None,
                            "actual_type_str": "None"
                        }
                        response.error_data.append(error_dict)
                continue

            # 型チェック
            type_mismatch = False
            expected_type_str = ""
            actual_type_str = type(value).__name__

            # 型の判定（Union/Optionalの処理）
            actual_expected_type = expected_type
            if hasattr(expected_type, '__origin__'):
                # Union[str, None] や Optional[str] の場合
                if expected_type.__origin__ is not type(None):
                    # Unionの引数からNone以外の型を取得
                    args = expected_type.__args__
                    if args:
                        # None以外の型を探す
                        actual_expected_type = next((arg for arg in args if arg is not type(None)), args[0])

            # date型のチェック
            if actual_expected_type == date:
                if not isinstance(value, date):
                    type_mismatch = True
                    expected_type_str = "date"

            # str型のチェック
            elif actual_expected_type == str:
                if not isinstance(value, str):
                    type_mismatch = True
                    expected_type_str = "str"
                else:
                    # 文字列の長さチェック
                    if max_length and len(value) > max_length:
                        response.error_codes.append("DATATYPE_CHECK_FAILED_LENGTH")
                        response.error_messages.append(
                            f"フィールド '{field_name}' の長さが最大値 {max_length} を超えています（実際: {len(value)}）"
                        )
                        error_dict = {
                            "field_name": field_name,
                            "max_length": str(max_length),
                            "expected_type_str": "str",
                            "actual_type_str": "str",
                            "actual_length": str(len(value))
                        }
                        response.error_data.append(error_dict)

            # その他の型（未対応の型）
            else:
                # 基本的な型チェック
                if not isinstance(value, actual_expected_type):
                    type_mismatch = True
                    expected_type_str = str(actual_expected_type)

            # 型の不一致がある場合
            if type_mismatch:
                response.error_codes.append("DATATYPE_CHECK_FAILED")
                response.error_messages.append(
                    f"フィールド '{field_name}' の型が一致しません。期待: {expected_type_str}, 実際: {actual_type_str}"
                )
                error_dict = {
                    "field_name": field_name,
                    "max_length": str(max_length) if max_length else None,
                    "expected_type_str": expected_type_str,
                    "actual_type_str": actual_type_str
                }
                response.error_data.append(error_dict)

    def _validate_time_logic(
        self,
        koujyou_master_data: KoujyouMasterBase,
        response: CheckIntegrityResponse
    ) -> None:
        """
        時間ロジックを検証する
        """
        if koujyou_master_data.start_operation_date >= koujyou_master_data.end_operation_date:
            response.error_codes.append("TIME_LOGIC_CHECK_INVALID")
            response.error_messages.append("運用開始日が運用終了日より後です")
            pk_conflicted = _format_pk_details(koujyou_master_data)
            response.error_data.append({"pk_conflicted": pk_conflicted})
            return

        logger.info(f"時間ロジックチェック開始: {koujyou_master_data.company_code} / {koujyou_master_data.previous_factory_code} / {koujyou_master_data.product_factory_code} / {koujyou_master_data.start_operation_date} / {koujyou_master_data.end_operation_date}")
        time_related_records = self.repository.get_time_related_records(koujyou_master_data)
        logger.info(f"時間ロジックチェック結果: {len(time_related_records)}件")
        if time_related_records:
            n_start = koujyou_master_data.start_operation_date
            n_end = koujyou_master_data.end_operation_date
            for record in time_related_records:
                r_start = record.start_operation_date
                r_end = record.end_operation_date
                if (
                    (n_start < r_start and n_start < r_end and n_end < r_start and n_end < r_end)
                    or
                    (n_start > r_start and n_start > r_end and n_end > r_start and n_end > r_end)

                ):
                    logger.info(f"時間ロジックが一致します: {record.company_code} / {record.previous_factory_code} / {record.product_factory_code} / {record.start_operation_date} / {record.end_operation_date}")
                else:
                    response.error_codes.append("TIME_LOGIC_CHECK_CONFLICTED")
                    response.error_messages.append(f"時間ロジックが一致しません: {record.company_code} / {record.previous_factory_code} / {record.product_factory_code} / {record.start_operation_date} / {record.end_operation_date}")
                    pk_conflicted = _format_pk_details(record)
                    response.error_data.append({"pk_conflicted": pk_conflicted})


    def check_integrity_2(
        self,
        koujyou_master_data: KoujyouMasterBase,
        pk_check: bool,
        datatype_check: bool,
        time_logic_check: bool,
    ) -> CheckIntegrityResponse:
        """
        Check the integrity of a record without datatype validations

        Args:
            koujyou_master_data: The record to check
            pk_check: Primary key check
            datatype_check: Datatype check
            time_logic_check: Time logic check

        Returns:
            CheckIntegrityResponse: The integrity check result
        """
        logger.info(
            f"Integrity check started: record={koujyou_master_data}, "
            f"pk_check={pk_check}, time_logic_check={time_logic_check}"
        )

        try:
            pk_detail = _format_pk_details(koujyou_master_data)
            response = CheckIntegrityResponse(
                error_codes=[],
                error_messages=[],
                pk_detail=pk_detail,
                error_data=[]
            )

            if pk_check:
                existing = self.repository.get_by_unique_keys(koujyou_master_data)
                if existing:
                    response.error_codes.append("PK_CHECK_FAILED")
                    response.error_messages.append("Primary key already exists")
                    response.error_data.append({})

            if time_logic_check:
                self._validate_time_logic(koujyou_master_data, response)

            return response

        except Exception as e:
            logger.error(f"Integrity check error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Integrity check error occurred"
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

