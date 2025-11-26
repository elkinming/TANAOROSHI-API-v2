"""
ユーザーサービス

ユーザーに関するビジネスロジック処理
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserBase, UserResponse
from app.constants.error_codes import ErrorCode, ErrorMessage
from app.utils.logger import get_logger


logger = get_logger(__name__)


class UserService:
    """ユーザーサービスクラス"""

    def __init__(self, session: Session):
        """
        サービスを初期化する

        Args:
            session: データベースセッション
        """
        self.repository = UserRepository(session)

    def get_all_users(
        self,
        search_keyword: Optional[str] = None
    ) -> List[UserResponse]:
        """
        ユーザーのリストを取得する

        Args:
            search_keyword: 全カラムで曖昧検索（オプション）

        Returns:
            List[UserResponse]: ユーザーのリスト
        """
        logger.debug(
            f"ユーザーリスト取得: search_keyword={search_keyword}"
        )

        db_items = self.repository.get_all(search_keyword=search_keyword)

        return [UserResponse.model_validate(item) for item in db_items]

    def create_user(self, user_data: UserBase) -> UserResponse:
        """
        ユーザーを作成する

        Args:
            user_data: 作成するユーザーデータ

        Returns:
            UserResponse: 作成されたユーザー

        Raises:
            HTTPException: 既に存在する場合、または作成エラーの場合
        """
        logger.info(f"ユーザー作成開始: {user_data}")

        # 既存データの確認
        exists = self.repository.get_by_id(user_data.id)
        if exists:
            logger.warning("ユーザーが既に存在します")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="既にユーザーが存在します"
            )

        try:
            db_item = self.repository.create_user(user_data)
            logger.info(f"ユーザー作成成功: {db_item}")
            return UserResponse.model_validate(db_item)
        except Exception as e:
            logger.error(f"ユーザー作成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーの作成中にエラーが発生しました"
            )

    def update_user(self, user_data: UserBase) -> UserResponse:
        """
        ユーザーを更新する

        Args:
            user_data: 更新するユーザーデータ

        Returns:
            UserResponse: 更新されたユーザー

        Raises:
            HTTPException: 見つからない場合、または更新エラーの場合
        """
        logger.info(f"ユーザー更新開始: {user_data}")

        try:
            db_item = self.repository.update_user(user_data)
            if not db_item:
                logger.warning("ユーザーが見つかりません（更新）")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ユーザーが見つかりません"
                )
            logger.info(f"ユーザー更新成功: {db_item}")
            return UserResponse.model_validate(db_item)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ユーザー更新エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーの更新中にエラーが発生しました"
            )

    def create_user_batch(self, user_data_list: List[UserBase]) -> List[UserResponse]:
        """
        ユーザーを一括作成する

        Args:
            user_data_list: 作成するユーザーデータのリスト

        Returns:
            List[UserResponse]: 作成されたユーザーのリスト

        Raises:
            HTTPException: 作成エラーの場合
        """
        logger.info(f"ユーザー一括作成開始: {len(user_data_list)}件")

        try:
            db_items = self.repository.create_user_batch(user_data_list)
            logger.info(f"ユーザー一括作成成功: {len(db_items)}件")
            return [UserResponse.model_validate(item) for item in db_items]

        except (IntegrityError, DataError) as e:
            # データベースの制約違反やデータエラーは400 Bad Request
            logger.warning(f"ユーザー一括作成データエラー: {e}")
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"データが無効です"
            )

        except DatabaseError as e:
            # その他のデータベースエラーは500 Internal Server Error
            logger.error(f"ユーザー一括作成データベースエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
            )

        except Exception as e:
            # 予期しないエラーは500 Internal Server Error
            logger.error(f"ユーザー一括作成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーの一括作成中にエラーが発生しました"
            )

    def update_user_batch(self, user_data_list: List[UserBase]) -> Dict[str, Any]:
        """
        ユーザーを一括更新する

        Args:
            user_data_list: 更新するユーザーデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[UserResponse] - 更新されたユーザーのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        logger.info(f"ユーザー一括更新開始: {len(user_data_list)}件")

        try:
            result = self.repository.update_user_batch(user_data_list)
            ok_records = result["ok_records"]
            error_records = result["error_records"]

            logger.info(
                f"ユーザー一括更新完了: 成功{len(ok_records)}件, エラー{len(error_records)}件"
            )

            return {
                "ok_records": [UserResponse.model_validate(item) for item in ok_records],
                "error_records": error_records
            }

        except (IntegrityError, DataError) as e:
            # データベースの制約違反やデータエラーは400 Bad Request
            logger.warning(f"ユーザー一括更新データエラー: {e}")
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"データが無効です"
            )

        except DatabaseError as e:
            # その他のデータベースエラーは500 Internal Server Error
            logger.error(f"ユーザー一括更新データベースエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
            )

        except Exception as e:
            # 予期しないエラーは500 Internal Server Error
            logger.error(f"ユーザー一括更新エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーの一括更新中にエラーが発生しました"
            )

    def create_multiple_user(self, user_data_list: List[UserBase]) -> Dict[str, Any]:
        """
        ユーザーを一括作成する

        Args:
            user_data_list: 作成するユーザーデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[UserResponse] - 作成されたユーザーのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        logger.info(f"ユーザー一括作成開始: {len(user_data_list)}件")

        try:
            print(user_data_list)
            result = self.repository.create_multiple_user(user_data_list)
            ok_records = result["ok_records"]
            error_records = result["error_records"]

            logger.info(
                f"ユーザー一括作成完了: 成功{len(ok_records)}件, エラー{len(error_records)}件"
            )

            return {
                "ok_records": [UserResponse.model_validate(item) for item in ok_records],
                "error_records": error_records
            }

        except (IntegrityError, DataError) as e:
            # データベースの制約違反やデータエラーは400 Bad Request
            logger.warning(f"ユーザー一括作成データエラー: {e}")
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"データが無効です"
            )

        except DatabaseError as e:
            # その他のデータベースエラーは500 Internal Server Error
            logger.error(f"ユーザー一括作成データベースエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
            )

        except Exception as e:
            # 予期しないエラーは500 Internal Server Error
            logger.error(f"ユーザー一括作成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーの一括作成中にエラーが発生しました"
            )

    def delete_multiple_user(self, user_data_list: List[UserBase]) -> Dict[str, Any]:
        """
        ユーザーを一括削除する

        Args:
            user_data_list: 削除するユーザーデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[UserResponse] - 削除されたユーザーのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        logger.info(f"ユーザー一括削除開始: {len(user_data_list)}件")

        try:
            result = self.repository.delete_multiple_user(user_data_list)
            ok_records = result["ok_records"]
            error_records = result["error_records"]

            logger.info(
                f"ユーザー一括削除完了: 成功{len(ok_records)}件, エラー{len(error_records)}件"
            )

            return {
                "ok_records": [UserResponse.model_validate(item) for item in ok_records],
                "error_records": error_records
            }

        except (IntegrityError, DataError) as e:
            # データベースの制約違反やデータエラーは400 Bad Request
            logger.warning(f"ユーザー一括削除データエラー: {e}")
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"データが無効です"
            )

        except DatabaseError as e:
            # その他のデータベースエラーは500 Internal Server Error
            logger.error(f"ユーザー一括削除データベースエラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
            )

        except Exception as e:
            # 予期しないエラーは500 Internal Server Error
            logger.error(f"ユーザー一括削除エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーの一括削除中にエラーが発生しました"
            )

