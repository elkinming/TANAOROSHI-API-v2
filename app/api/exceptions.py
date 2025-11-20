"""
API例外ハンドラー

統一されたエラーレスポンス形式を提供
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from app.schemas.response import ApiResponse
from app.constants.error_codes import ErrorCode, ErrorMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTPExceptionを統一されたレスポンス形式に変換する
    
    Args:
        request: リクエストオブジェクト
        exc: HTTPException
        
    Returns:
        JSONResponse: 統一されたエラーレスポンス
    """
    logger.warning(
        f"HTTPエラー発生: {exc.status_code} - {exc.detail} - "
        f"Path: {request.url.path}"
    )
    
    response = ApiResponse.error(
        message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(exclude_none=True)
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    バリデーションエラーを統一されたレスポンス形式に変換する
    
    Args:
        request: リクエストオブジェクト
        exc: RequestValidationError
        
    Returns:
        JSONResponse: 統一されたエラーレスポンス
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"バリデーションエラー発生: {errors} - Path: {request.url.path}"
    )
    
    response = ApiResponse.error(
        message=ErrorMessage.get_message(ErrorCode.VALIDATION_ERROR),
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code=ErrorCode.VALIDATION_ERROR.value,
        details={"errors": errors}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(exclude_none=True)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    一般的な例外を統一されたレスポンス形式に変換する
    
    Args:
        request: リクエストオブジェクト
        exc: Exception
        
    Returns:
        JSONResponse: 統一されたエラーレスポンス
    """
    logger.error(
        f"予期しないエラー発生: {type(exc).__name__} - {str(exc)} - "
        f"Path: {request.url.path}",
        exc_info=True
    )
    
    response = ApiResponse.error(
        message=ErrorMessage.get_message(ErrorCode.INTERNAL_SERVER_ERROR),
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(exclude_none=True)
    )

