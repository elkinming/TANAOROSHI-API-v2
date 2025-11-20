"""
エラーコード定義

統一されたエラーコードとメッセージの定義
"""
from enum import Enum
from typing import Dict, Optional


class ErrorCode(str, Enum):
    """エラーコード定義"""
    # 共通エラー
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    
    # 得意先マスタ関連エラー
    CUSTOM_MASTER_NOT_FOUND = "CUSTOM_MASTER_NOT_FOUND"
    CUSTOM_MASTER_ALREADY_EXISTS = "CUSTOM_MASTER_ALREADY_EXISTS"
    CUSTOM_MASTER_CREATE_FAILED = "CUSTOM_MASTER_CREATE_FAILED"
    CUSTOM_MASTER_UPDATE_FAILED = "CUSTOM_MASTER_UPDATE_FAILED"
    CUSTOM_MASTER_DELETE_FAILED = "CUSTOM_MASTER_DELETE_FAILED"


class ErrorMessage:
    """エラーメッセージ定義"""
    
    # 共通エラーメッセージ
    VALIDATION_ERROR = "リクエストのバリデーションに失敗しました"
    INTERNAL_SERVER_ERROR = "サーバー内部エラーが発生しました"
    NOT_FOUND = "リソースが見つかりません"
    CONFLICT = "リソースが既に存在します"
    BAD_REQUEST = "不正なリクエストです"
    UNAUTHORIZED = "認証が必要です"
    FORBIDDEN = "アクセス権限がありません"
    
    # 得意先マスタ関連エラーメッセージ
    CUSTOM_MASTER_NOT_FOUND = "得意先マスタが見つかりません"
    CUSTOM_MASTER_ALREADY_EXISTS = "得意先マスタが既に存在します"
    CUSTOM_MASTER_CREATE_FAILED = "得意先マスタの作成に失敗しました"
    CUSTOM_MASTER_UPDATE_FAILED = "得意先マスタの更新に失敗しました"
    CUSTOM_MASTER_DELETE_FAILED = "得意先マスタの削除に失敗しました"
    
    @classmethod
    def get_message(cls, error_code: ErrorCode, detail: Optional[str] = None) -> str:
        """
        エラーコードに対応するメッセージを取得する
        
        Args:
            error_code: エラーコード
            detail: 追加の詳細情報（オプション）
            
        Returns:
            str: エラーメッセージ
        """
        message_map: Dict[ErrorCode, str] = {
            ErrorCode.VALIDATION_ERROR: cls.VALIDATION_ERROR,
            ErrorCode.INTERNAL_SERVER_ERROR: cls.INTERNAL_SERVER_ERROR,
            ErrorCode.NOT_FOUND: cls.NOT_FOUND,
            ErrorCode.CONFLICT: cls.CONFLICT,
            ErrorCode.BAD_REQUEST: cls.BAD_REQUEST,
            ErrorCode.UNAUTHORIZED: cls.UNAUTHORIZED,
            ErrorCode.FORBIDDEN: cls.FORBIDDEN,
            ErrorCode.CUSTOM_MASTER_NOT_FOUND: cls.CUSTOM_MASTER_NOT_FOUND,
            ErrorCode.CUSTOM_MASTER_ALREADY_EXISTS: cls.CUSTOM_MASTER_ALREADY_EXISTS,
            ErrorCode.CUSTOM_MASTER_CREATE_FAILED: cls.CUSTOM_MASTER_CREATE_FAILED,
            ErrorCode.CUSTOM_MASTER_UPDATE_FAILED: cls.CUSTOM_MASTER_UPDATE_FAILED,
            ErrorCode.CUSTOM_MASTER_DELETE_FAILED: cls.CUSTOM_MASTER_DELETE_FAILED,
        }
        
        base_message = message_map.get(error_code, cls.INTERNAL_SERVER_ERROR)
        
        if detail:
            return f"{base_message}: {detail}"
        
        return base_message


class SuccessMessage:
    """成功メッセージ定義"""
    
    # 共通成功メッセージ
    OPERATION_SUCCESS = "処理が正常に完了しました"
    
    # 得意先マスタ関連成功メッセージ
    CUSTOM_MASTER_CREATED = "得意先マスタを作成しました"
    CUSTOM_MASTER_RETRIEVED = "得意先マスタを取得しました"
    CUSTOM_MASTER_LIST_RETRIEVED = "得意先マスタの取得が完了しました"
    CUSTOM_MASTER_UPDATED = "得意先マスタを更新しました"
    CUSTOM_MASTER_DELETED = "得意先マスタを削除しました"

