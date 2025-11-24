"""
APIレスポンススキーマ

統一されたAPIレスポンス形式を定義
"""
from typing import Dict, Optional, Generic, TypeVar, List, Any
from pydantic import BaseModel, Field
from app.schemas.koujyou_master import KoujyouMasterBase

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    統一されたAPIレスポンス形式

    成功時とエラー時の両方に対応する標準的なレスポンス形式
    """
    code: int = Field(..., description="ステータスコード（HTTPステータスコード）")
    message: str = Field(..., description="レスポンスメッセージ")
    data: Optional[T] = Field(None, description="レスポンスデータ（成功時）")
    error: Optional[dict] = Field(None, description="エラー情報（エラー時）")

    @classmethod
    def success(
        cls,
        data: T,
        message: str = "処理が正常に完了しました",
        code: int = 200
    ) -> "ApiResponse[T]":
        """
        成功レスポンスを作成する

        Args:
            data: レスポンスデータ
            message: レスポンスメッセージ
            code: HTTPステータスコード

        Returns:
            ApiResponse: 成功レスポンス
        """
        return cls(
            code=code,
            message=message,
            data=data,
            error=None
        )

    @classmethod
    def create_error(
        cls,
        message: str,
        code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        # error_list: Optional[T] = None
    ) -> "ApiResponse[None]":
        """
        エラーレスポンスを作成する

        Args:
            message: エラーメッセージ
            code: HTTPステータスコード
            error_code: エラーコード（オプション）
            details: エラー詳細情報（オプション）
            error_list: エラーレコードのリスト（オプション）

        Returns:
            ApiResponse: エラーレスポンス
        """
        error_info = {}
        if error_code:
            error_info["error_code"] = error_code
        if details:
            error_info["details"] = details
        # if error_list:
        #     error_info["errorList"] = error_list

        return cls(
            code=code,
            message=message,
            data=None,
            error=error_info if error_info else None
        )


class ListResponse(BaseModel, Generic[T]):
    """
    リストレスポンス用のデータ構造

    ページネーション情報を含むリストレスポンス
    """
    items: List[T] = Field(..., description="データリスト")
    total: Optional[int] = Field(None, description="総件数")
    skip: int = Field(0, description="スキップ件数")
    limit: int = Field(100, description="取得件数")

