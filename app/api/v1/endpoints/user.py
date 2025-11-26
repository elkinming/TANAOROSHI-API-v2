"""
ユーザーAPIエンドポイント

ユーザーのCRUD操作を提供するRESTful API
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlmodel import Session
from app.database import get_session
from app.services.user_service import UserService
from app.schemas.user import UserBase, UserResponse
from app.schemas.response import ApiResponse, ListResponse
from app.constants.error_codes import SuccessMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/user", tags=["ユーザー"])


def get_service(session: Session = Depends(get_session)) -> UserService:
    """
    サービスインスタンスを取得する

    Args:
        session: データベースセッション

    Returns:
        UserService: サービスインスタンス
    """
    return UserService(session)


@router.get(
    "/list",
    response_model=ApiResponse[ListResponse[UserResponse]],
    summary="ユーザー一覧を取得",
    description="ユーザーのリストを取得します"
)
async def get_user_list(
    search_keyword: Optional[str] = Query(None, description="全カラムで曖昧検索（オプション）"),
    service: UserService = Depends(get_service)
) -> ApiResponse[ListResponse[UserResponse]]:
    """
    ユーザーのリストを取得する

    Args:
        search_keyword: 全カラムで曖昧検索（オプション）
        service: サービスインスタンス

    Returns:
        ApiResponse[ListResponse[UserResponse]]: ユーザーのリスト
    """
    items = service.get_all_users(search_keyword=search_keyword)

    list_response = ListResponse(
        items=items
    )

    return ApiResponse.success(
        data=list_response,
        message=SuccessMessage.USER_LIST_RETRIEVED
    )


@router.post(
    "",
    response_model=ApiResponse[UserResponse],
    summary="ユーザー作成",
    description="新しいユーザーを作成します"
)
async def create_user(
    user_data: UserBase,
    service: UserService = Depends(get_service)
) -> ApiResponse[UserResponse]:
    """
    ユーザーを作成する

    Args:
        user_data: 作成するユーザーデータ
        service: サービスインスタンス

    Returns:
        ApiResponse[UserResponse]: 作成されたユーザー
    """
    result = service.create_user(user_data)
    return ApiResponse.success(
        data=result,
        message=SuccessMessage.USER_CREATED
    )


@router.put(
    "",
    response_model=ApiResponse[UserResponse],
    summary="ユーザー更新",
    description="ユーザーを更新します"
)
async def update_user(
    user_data: UserBase,
    service: UserService = Depends(get_service)
) -> ApiResponse[UserResponse]:
    """
    ユーザーを更新する

    Args:
        user_data: 更新するユーザーデータ
        service: サービスインスタンス

    Returns:
        ApiResponse[UserResponse]: 更新されたユーザー
    """
    result = service.update_user(user_data)
    return ApiResponse.success(
        data=result,
        message=SuccessMessage.USER_UPDATED
    )


@router.post(
    "/list",
    response_model=ApiResponse[Dict[str, Any]],
    summary="ユーザー一括作成",
    description="複数のユーザーを一括で作成します"
)
async def create_user_list(
    user_data_list: List[UserBase],
    response: Response,
    service: UserService = Depends(get_service)
) -> ApiResponse[Dict[str, Any]]:
    """
    ユーザーを一括作成する

    Args:
        user_data_list: 作成するユーザーデータのリスト
        service: サービスインスタンス
        response: FastAPI Response object for setting status code

    Returns:
        ApiResponse[Dict[str, Any]]: 辞書型で以下のキーを含む:
            - ok_records: List[UserResponse] - 作成されたユーザーのリスト
            - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
    """
    result = service.create_multiple_user(user_data_list)

    # Check if result has error_records and it's not empty
    if result.get("error_records"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse.create_error(
            message="ユーザーの一括作成中にエラーが発生しました",
            code=status.HTTP_400_BAD_REQUEST,
            error_code="",
            details=result
        )

    return ApiResponse.success(
        data=result,
        message=SuccessMessage.USER_BATCH_CREATED
    )


@router.put(
    "/list",
    response_model=ApiResponse[Dict[str, Any]],
    summary="ユーザー一括更新",
    description="複数のユーザーを一括で更新します"
)
async def update_user_list(
    user_data_list: List[UserBase],
    response: Response,
    service: UserService = Depends(get_service)
) -> ApiResponse[Dict[str, Any]]:
    """
    ユーザーを一括更新する

    Args:
        user_data_list: 更新するユーザーデータのリスト
        service: サービスインスタンス
        response: FastAPI Response object for setting status code

    Returns:
        ApiResponse[Dict[str, Any]]: 辞書型で以下のキーを含む:
            - ok_records: List[UserResponse] - 更新されたユーザーのリスト
            - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
    """
    result = service.update_user_batch(user_data_list)

    # Check if result has error_records and it's not empty
    if result.get("error_records"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse.create_error(
            message="ユーザーの一括更新中にエラーが発生しました",
            code=status.HTTP_400_BAD_REQUEST,
            error_code="",
            details=result
        )

    return ApiResponse.success(
        data=result,
        message=SuccessMessage.USER_BATCH_UPDATED
    )


@router.delete(
    "/list",
    response_model=ApiResponse[Dict[str, Any]],
    summary="ユーザー一括削除",
    description="複数のユーザーを一括で削除します"
)
async def delete_user_list(
    user_data_list: List[UserBase],
    response: Response,
    service: UserService = Depends(get_service)
) -> ApiResponse[Dict[str, Any]]:
    """
    ユーザーを一括削除する

    Args:
        user_data_list: 削除するユーザーデータのリスト
        service: サービスインスタンス
        response: FastAPI Response object for setting status code

    Returns:
        ApiResponse[Dict[str, Any]]: 辞書型で以下のキーを含む:
            - ok_records: List[UserResponse] - 削除されたユーザーのリスト
            - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
    """
    result = service.delete_multiple_user(user_data_list)

    # Check if result has error_records and it's not empty
    if result.get("error_records"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse.create_error(
            message="ユーザーの一括削除中にエラーが発生しました",
            code=status.HTTP_400_BAD_REQUEST,
            error_code="",
            details=result
        )

    return ApiResponse.success(
        data=result,
        message=SuccessMessage.USER_BATCH_DELETED
    )

