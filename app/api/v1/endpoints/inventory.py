"""
得意先マスタAPIエンドポイント

得意先マスタのCRUD操作を提供するRESTful API
"""
from datetime import date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlmodel import Session
from app.database import get_session
from app.services.custom_master_service import CustomMasterService
from app.services.inventory_service import InventoryService
from app.schemas.koujyou_master import KoujyouMasterBase, KoujyouMasterResponse
from app.schemas.custom_master import (
    CustomMasterCreate,
    CustomMasterUpdate,
    CustomMasterResponse
)
from app.schemas.response import ApiResponse, ListResponse
from app.constants.error_codes import SuccessMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/inventory", tags=["工場マスタ"])


def get_service(session: Session = Depends(get_session)) -> InventoryService:
    """
    サービスインスタンスを取得する

    Args:
        session: データベースセッション

    Returns:
        CustomMasterService: サービスインスタンス
    """
    return InventoryService(session)


@router.get(
    "/record-list",
    response_model=ApiResponse[ListResponse[KoujyouMasterBase]],
    summary="工場マスタ一覧を取得",
    description="工場マスタのリストを取得します"
)
async def get_record_list(
    previous_factory_code: Optional[str] = Query(None, description="従来工場コードでフィルタ（オプション）"),
    product_factory_code: Optional[str] = Query(None, description="商品工場コードでフィルタ（オプション）"),
    search_keyword: Optional[str] = Query(None, description="全カラムで曖昧検索（オプション）"),

    service: InventoryService = Depends(get_service)
) -> ApiResponse[ListResponse[KoujyouMasterBase]]:
    """
    工場マスタのリストを取得する

    Args:
        previous_factory_code: 従来工場コードでフィルタ（オプション）
        product_factory_code: 商品工場コードでフィルタ（オプション）
        search_keyword: 全カラムで曖昧検索（オプション）
        service: サービスインスタンス

    Returns:
        ApiResponse[ListResponse[KoujyouMasterBase]]: 工場マスタのリスト
    """
    items = service.get_koujyou_master_all(
        previous_factory_code=previous_factory_code,
        product_factory_code=product_factory_code,
        search_keyword=search_keyword
    )

    list_response = ListResponse(
        items=items
    )

    return ApiResponse.success(
        data=list_response,
        message=SuccessMessage.KOUJYOU_MASTER_CREATED
    )


@router.post(
    "/record",
    response_model=ApiResponse[KoujyouMasterResponse],
    summary="工場マスタ作成",
    description="新しい工場マスタを作成します"
)
async def create_koujyou_master(
    koujyou_master_data: KoujyouMasterBase,
    service: InventoryService = Depends(get_service)
) -> ApiResponse[KoujyouMasterResponse]:
    """
    工場マスタを作成する

    Args:
        koujyou_master_data: 作成する工場マスタデータ
        service: サービスインスタンス

    Returns:
        ApiResponse[KoujyouMasterResponse]: 作成された工場マスタ
    """
    result = service.create_koujyou_master(koujyou_master_data)
    return ApiResponse.success(
        data=result,
        message=SuccessMessage.KOUJYOU_MASTER_CREATED
    )


@router.put(
    "/record",
    response_model=ApiResponse[KoujyouMasterResponse],
    summary="工場マスタ更新",
    description="工場マスタを更新します"
)
async def update_koujyou_master(
    koujyou_master_data: KoujyouMasterBase,
    service: InventoryService = Depends(get_service)
) -> ApiResponse[KoujyouMasterResponse]:
    """
    工場マスタを更新する

    Args:
        koujyou_master_data: 更新する工場マスタデータ
        service: サービスインスタンス

    Returns:
        ApiResponse[KoujyouMasterResponse]: 更新された工場マスタ
    """
    result = service.update_koujyou_master(koujyou_master_data)
    return ApiResponse.success(
        data=result,
        message=SuccessMessage.KOUJYOU_MASTER_UPDATED
    )


@router.post(
    "/record-batch",
    response_model=ApiResponse[List[KoujyouMasterResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="工場マスタ一括作成",
    description="複数の工場マスタを一括で作成します"
)
async def create_koujyou_master_batch(
    koujyou_master_data_list: List[KoujyouMasterBase],
    service: InventoryService = Depends(get_service)
) -> ApiResponse[List[KoujyouMasterResponse]]:
    """
    工場マスタを一括作成する

    Args:
        koujyou_master_data_list: 作成する工場マスタデータのリスト
        service: サービスインスタンス

    Returns:
        ApiResponse[List[KoujyouMasterResponse]]: 作成された工場マスタのリスト
    """
    result = service.create_koujyou_master_batch(koujyou_master_data_list)
    return ApiResponse.success(
        data=result,
        message=SuccessMessage.KOUJYOU_MASTER_BATCH_CREATED,
        code=status.HTTP_201_CREATED
    )


@router.put(
    "/record/multiple",
    response_model=ApiResponse[Dict[str, Any]],
    summary="工場マスタ一括更新",
    description="複数の工場マスタを一括で更新します"
)
async def update_koujyou_master_batch(
    koujyou_master_data_list: List[KoujyouMasterBase],
    response: Response,
    service: InventoryService = Depends(get_service)
) -> ApiResponse[Dict[str, Any]]:
    """
    工場マスタを一括更新する

    Args:
        koujyou_master_data_list: 更新する工場マスタデータのリスト
        service: サービスインスタンス
        response: FastAPI Response object for setting status code

    Returns:
        ApiResponse[Dict[str, Any]]: 辞書型で以下のキーを含む:
            - ok_records: List[KoujyouMasterResponse] - 更新された工場マスタのリスト
            - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
    """
    result = service.update_koujyou_master_batch(koujyou_master_data_list)

    # Check if result has error_records and it's not empty
    if result.get("error_records"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse.create_error(
            message="工場マスタの一括更新中にエラーが発生しました",
            code=status.HTTP_400_BAD_REQUEST,
            error_code="",
            details=result
        )

    return ApiResponse.success(
        data=result,
        message=SuccessMessage.KOUJYOU_MASTER_BATCH_UPDATED
    )


@router.post(
    "/record/multiple",
    response_model=ApiResponse[Dict[str, Any]],
    summary="工場マスタ一括作成",
    description="複数の工場マスタを一括で作成します"
)
async def create_multiple_koujyou_master(
    koujyou_master_data_list: List[KoujyouMasterBase],
    response: Response,
    service: InventoryService = Depends(get_service)
) -> ApiResponse[Dict[str, Any]]:
    """
    工場マスタを一括作成する

    Args:
        koujyou_master_data_list: 作成する工場マスタデータのリスト
        service: サービスインスタンス
        response: FastAPI Response object for setting status code

    Returns:
        ApiResponse[Dict[str, Any]]: 辞書型で以下のキーを含む:
            - ok_records: List[KoujyouMasterResponse] - 作成された工場マスタのリスト
            - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
    """
    result = service.create_multiple_koujyou_master(koujyou_master_data_list)

    # Check if result has error_records and it's not empty
    if result.get("error_records"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse.create_error(
            message="工場マスタの一括作成中にエラーが発生しました",
            code=status.HTTP_400_BAD_REQUEST,
            error_code="",
            details=result
        )

    return ApiResponse.success(
        data=result,
        message=SuccessMessage.KOUJYOU_MASTER_BATCH_CREATED
    )


@router.delete(
    "/record/multiple",
    response_model=ApiResponse[Dict[str, Any]],
    summary="工場マスタ一括削除",
    description="複数の工場マスタを一括で削除します"
)
async def delete_multiple_koujyou_master(
    koujyou_master_data_list: List[KoujyouMasterBase],
    response: Response,
    service: InventoryService = Depends(get_service)
) -> ApiResponse[Dict[str, Any]]:
    """
    工場マスタを一括削除する

    Args:
        koujyou_master_data_list: 削除する工場マスタデータのリスト
        service: サービスインスタンス
        response: FastAPI Response object for setting status code

    Returns:
        ApiResponse[Dict[str, Any]]: 辞書型で以下のキーを含む:
            - ok_records: List[KoujyouMasterResponse] - 削除された工場マスタのリスト
            - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
    """
    result = service.delete_multiple_koujyou_master(koujyou_master_data_list)

    # Check if result has error_records and it's not empty
    if result.get("error_records"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse.create_error(
            message="工場マスタの一括削除中にエラーが発生しました",
            code=status.HTTP_400_BAD_REQUEST,
            error_code="",
            details=result
        )

    return ApiResponse.success(
        data=result,
        message=SuccessMessage.KOUJYOU_MASTER_BATCH_DELETED
    )





# @router.post(
#     "/record",
#     response_model=ApiResponse[CustomMasterResponse],
#     status_code=status.HTTP_201_CREATED,
#     summary="工場マスタ作成",
#     description="新しい工場マスタ作成します"
# )
# async def create_record(
#     koujyou_master_data: KoujyouMasterBase,
#     service: InventoryService = Depends(get_service)
# ) -> ApiResponse[KoujyouMasterResponse]:
#     """
#     工場マスタを作成する

#     Args:
#         koujyou_master_data: 作成する工場マスタデータ
#         service: サービスインスタンス

#     Returns:
#         ApiResponse[KoujyouMasterResponse]: 作成された工場マスタ
#     """
#     result = service.create_custom_master(custom_master_data)
#     return ApiResponse.success(
#         data=result,
#         message=SuccessMessage.CUSTOM_MASTER_CREATED,
#         code=status.HTTP_201_CREATED
#     )

# @router.put(
#     "/{corporate_cd}/{toku_cd}/{ty_date_from}",
#     response_model=ApiResponse[CustomMasterResponse],
#     summary="得意先マスタ更新",
#     description="得意先マスタを更新します"
# )
# async def update_custom_master(
#     corporate_cd: str,
#     toku_cd: str,
#     ty_date_from: date,
#     custom_master_data: CustomMasterUpdate,
#     service: CustomMasterService = Depends(get_service)
# ) -> ApiResponse[CustomMasterResponse]:
#     """
#     得意先マスタを更新する

#     Args:
#         corporate_cd: 法人コード
#         toku_cd: 得意先コード
#         ty_date_from: 適用開始日
#         custom_master_data: 更新するデータ
#         service: サービスインスタンス

#     Returns:
#         ApiResponse[CustomMasterResponse]: 更新された得意先マスタ
#     """
#     result = service.update_custom_master(
#         corporate_cd,
#         toku_cd,
#         ty_date_from,
#         custom_master_data
#     )
#     return ApiResponse.success(
#         data=result,
#         message=SuccessMessage.CUSTOM_MASTER_UPDATED
#     )


# @router.delete(
#     "/{corporate_cd}/{toku_cd}/{ty_date_from}",
#     response_model=ApiResponse[None],
#     summary="得意先マスタ削除",
#     description="得意先マスタを削除します"
# )
# async def delete_custom_master(
#     corporate_cd: str,
#     toku_cd: str,
#     ty_date_from: date,
#     service: CustomMasterService = Depends(get_service)
# ) -> ApiResponse[None]:
#     """
#     得意先マスタを削除する

#     Args:
#         corporate_cd: 法人コード
#         toku_cd: 得意先コード
#         ty_date_from: 適用開始日
#         service: サービスインスタンス

#     Returns:
#         ApiResponse[None]: 削除成功レスポンス
#     """
#     service.delete_custom_master(corporate_cd, toku_cd, ty_date_from)
#     return ApiResponse.success(
#         data=None,
#         message=SuccessMessage.CUSTOM_MASTER_DELETED
#     )

