"""
API例外ハンドラー

統一されたエラーレスポンス形式を提供
"""
import json
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
    try:
        path = request.url.path if hasattr(request, 'url') and request.url else "unknown"
        logger.warning(
            f"HTTPエラー発生: {exc.status_code} - {exc.detail} - "
            f"Path: {path}"
        )
        print("Step 1")
        detail_message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        print("Step 2")
        response = ApiResponse.create_error(
            message=detail_message,
            code=exc.status_code,
            error_code=f"HTTP_{exc.status_code}"
        )
        print("Step 3")
        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump(exclude_none=True)
        )
    except Exception as handler_error:
        # ハンドラー内でエラーが発生した場合のフォールバック
        logger.error(
            f"HTTP例外ハンドラー内でエラー発生: {handler_error.__str__()}",
            exc_info=True
        )
        # シンプルなエラーレスポンスを返す
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
                "error": {"error_code": f"HTTP_{exc.status_code}"}
            }
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
    try:
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })

        # リクエストボディを取得（ログ用）
        request_body = None
        try:
            # JSONボディを取得
            if request.method in ["POST", "PUT", "PATCH"]:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        request_body = json.loads(body_bytes.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # JSONでない場合は文字列として保存
                        request_body = body_bytes.decode('utf-8', errors='replace')
        except Exception as body_error:
            # ボディの読み取りに失敗した場合（既に読み取られているなど）
            logger.debug(f"リクエストボディの読み取りに失敗: {body_error}")

        logger.warning(
            f"バリデーションエラー発生: {errors} - Path: {request.url.path} - "
            f"Method: {request.method} - Body: {request_body}"
        )

        response = ApiResponse.create_error(
            message=ErrorMessage.get_message(ErrorCode.VALIDATION_ERROR),
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=ErrorCode.VALIDATION_ERROR.value,
            details={"errors": errors}
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(exclude_none=True)
        )
    except Exception as handler_error:
        # ハンドラー内でエラーが発生した場合のフォールバック
        logger.error(
            f"バリデーション例外ハンドラー内でエラー発生: {handler_error.__str__()}",
            exc_info=True
        )
        # シンプルなエラーレスポンスを返す
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "バリデーションエラーが発生しました",
                "error": {"error_code": ErrorCode.VALIDATION_ERROR.value}
            }
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

    response = ApiResponse.create_error(
        message=ErrorMessage.get_message(ErrorCode.INTERNAL_SERVER_ERROR),
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(exclude_none=True)
    )

