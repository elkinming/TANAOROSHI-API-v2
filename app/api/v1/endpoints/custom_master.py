"""
得意先マスタAPIエンドポイント

得意先マスタのCRUD操作を提供するRESTful API
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from app.database import get_session
from app.services.custom_master_service import CustomMasterService
from app.schemas.custom_master import (
    CustomMasterCreate,
    CustomMasterUpdate,
    CustomMasterResponse
)
from app.schemas.response import ApiResponse, ListResponse
from app.constants.error_codes import SuccessMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/custom-masters", tags=["得意先マスタ"])


def get_service(session: Session = Depends(get_session)) -> CustomMasterService:
    """
    サービスインスタンスを取得する
    
    Args:
        session: データベースセッション
        
    Returns:
        CustomMasterService: サービスインスタンス
    """
    return CustomMasterService(session)


@router.post(
    "/",
    response_model=ApiResponse[CustomMasterResponse],
    status_code=status.HTTP_201_CREATED,
    summary="得意先マスタ作成",
    description="新しい得意先マスタを作成します"
)
async def create_custom_master(
    custom_master_data: CustomMasterCreate,
    service: CustomMasterService = Depends(get_service)
) -> ApiResponse[CustomMasterResponse]:
    """
    得意先マスタを作成する
    
    Args:
        custom_master_data: 作成する得意先マスタデータ
        service: サービスインスタンス
        
    Returns:
        ApiResponse[CustomMasterResponse]: 作成された得意先マスタ
    """
    result = service.create_custom_master(custom_master_data)
    return ApiResponse.success(
        data=result,
        message=SuccessMessage.CUSTOM_MASTER_CREATED,
        code=status.HTTP_201_CREATED
    )


@router.get(
    "/",
    response_model=ApiResponse[ListResponse[CustomMasterResponse]],
    summary="得意先マスタ一覧取得",
    description="得意先マスタのリストを取得します"
)
async def get_custom_masters(
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する最大件数"),
    corporate_cd: Optional[str] = Query(None, description="法人コードでフィルタ"),
    toku_cd: Optional[str] = Query(None, description="得意先コードでフィルタ"),
    toku_name: Optional[str] = Query(None, description="得意先名称で曖昧検索"),
    service: CustomMasterService = Depends(get_service)
) -> ApiResponse[ListResponse[CustomMasterResponse]]:
    """
    得意先マスタのリストを取得する
    
    Args:
        skip: スキップする件数
        limit: 取得する最大件数
        corporate_cd: 法人コードでフィルタ（オプション）
        toku_cd: 得意先コードでフィルタ（オプション）
        toku_name: 得意先名称で曖昧検索（オプション）
        service: サービスインスタンス
        
    Returns:
        ApiResponse[ListResponse[CustomMasterResponse]]: 得意先マスタのリスト
    """
    items = service.get_custom_masters(
        skip=skip,
        limit=limit,
        corporate_cd=corporate_cd,
        toku_cd=toku_cd,
        toku_name=toku_name
    )
    
    list_response = ListResponse(
        items=items,
        skip=skip,
        limit=limit
    )
    
    return ApiResponse.success(
        data=list_response,
        message=SuccessMessage.CUSTOM_MASTER_LIST_RETRIEVED
    )


@router.get(
    "/{corporate_cd}/{toku_cd}/{ty_date_from}",
    response_model=ApiResponse[CustomMasterResponse],
    summary="得意先マスタ取得",
    description="指定された主キーで得意先マスタを取得します"
)
async def get_custom_master(
    corporate_cd: str,
    toku_cd: str,
    ty_date_from: date,
    service: CustomMasterService = Depends(get_service)
) -> ApiResponse[CustomMasterResponse]:
    """
    得意先マスタを取得する
    
    Args:
        corporate_cd: 法人コード
        toku_cd: 得意先コード
        ty_date_from: 適用開始日
        service: サービスインスタンス
        
    Returns:
        ApiResponse[CustomMasterResponse]: 得意先マスタ
    """
    result = service.get_custom_master(corporate_cd, toku_cd, ty_date_from)
    return ApiResponse.success(
        data=result,
        message=SuccessMessage.CUSTOM_MASTER_RETRIEVED
    )


@router.put(
    "/{corporate_cd}/{toku_cd}/{ty_date_from}",
    response_model=ApiResponse[CustomMasterResponse],
    summary="得意先マスタ更新",
    description="得意先マスタを更新します"
)
async def update_custom_master(
    corporate_cd: str,
    toku_cd: str,
    ty_date_from: date,
    custom_master_data: CustomMasterUpdate,
    service: CustomMasterService = Depends(get_service)
) -> ApiResponse[CustomMasterResponse]:
    """
    得意先マスタを更新する
    
    Args:
        corporate_cd: 法人コード
        toku_cd: 得意先コード
        ty_date_from: 適用開始日
        custom_master_data: 更新するデータ
        service: サービスインスタンス
        
    Returns:
        ApiResponse[CustomMasterResponse]: 更新された得意先マスタ
    """
    result = service.update_custom_master(
        corporate_cd,
        toku_cd,
        ty_date_from,
        custom_master_data
    )
    return ApiResponse.success(
        data=result,
        message=SuccessMessage.CUSTOM_MASTER_UPDATED
    )


@router.delete(
    "/{corporate_cd}/{toku_cd}/{ty_date_from}",
    response_model=ApiResponse[None],
    summary="得意先マスタ削除",
    description="得意先マスタを削除します"
)
async def delete_custom_master(
    corporate_cd: str,
    toku_cd: str,
    ty_date_from: date,
    service: CustomMasterService = Depends(get_service)
) -> ApiResponse[None]:
    """
    得意先マスタを削除する
    
    Args:
        corporate_cd: 法人コード
        toku_cd: 得意先コード
        ty_date_from: 適用開始日
        service: サービスインスタンス
        
    Returns:
        ApiResponse[None]: 削除成功レスポンス
    """
    service.delete_custom_master(corporate_cd, toku_cd, ty_date_from)
    return ApiResponse.success(
        data=None,
        message=SuccessMessage.CUSTOM_MASTER_DELETED
    )

