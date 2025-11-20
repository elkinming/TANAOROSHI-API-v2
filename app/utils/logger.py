"""
ログ設定ユーティリティ

Loguruを使用したログ設定
自動ローテーション、色付き出力、例外トレースバックなどの機能を提供
"""
import sys
from typing import Optional
from pathlib import Path
from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    max_bytes: Optional[int] = None,
    backup_count: int = 5,
    when: Optional[str] = None
) -> None:
    """
    ログ設定を初期化する（Loguruを使用）
    
    Args:
        log_level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: ログファイルパス（指定しない場合は標準出力のみ）
        log_format: ログフォーマット（デフォルトは標準フォーマット）
        max_bytes: ログファイルの最大サイズ（バイト）。指定するとサイズベースのローテーションが有効
        backup_count: 保持するバックアップファイル数（デフォルト: 5）
        when: 日付ベースのローテーション間隔（'S', 'M', 'H', 'D', 'W0'-'W6', 'midnight'）
              指定すると日付ベースのローテーションが有効
    """
    # 既存のハンドラーを削除
    logger.remove()
    
    # デフォルトフォーマット
    if log_format is None:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    # 標準出力へのログ出力（色付き）
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level.upper(),
        colorize=True,
        backtrace=True,  # 例外の詳細なトレースバック
        diagnose=True  # 変数の値を表示
    )
    
    # ファイルログが指定されている場合
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ファイル出力用のフォーマット（色なし）
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
        
        # ローテーション設定
        rotation = None
        retention = backup_count
        
        if when:
            # 日付ベースのローテーション
            rotation = when  # 'D' = 日次, 'H' = 時間, 'midnight' = 日次深夜
        elif max_bytes:
            # サイズベースのローテーション
            # loguruは "10 MB", "500 KB" などの形式を期待
            if max_bytes >= 1024 * 1024 * 1024:  # GB
                rotation = f"{max_bytes / (1024 * 1024 * 1024):.1f} GB"
            elif max_bytes >= 1024 * 1024:  # MB
                rotation = f"{max_bytes / (1024 * 1024):.1f} MB"
            elif max_bytes >= 1024:  # KB
                rotation = f"{max_bytes / 1024:.1f} KB"
            else:
                rotation = f"{max_bytes} B"
        
        logger.add(
            log_file,
            format=file_format,
            level=log_level.upper(),
            rotation=rotation,
            retention=retention,
            compression="zip",  # 古いログファイルを自動的に圧縮
            encoding="utf-8",
            backtrace=True,
            diagnose=True
        )
    
    # サードパーティライブラリのログレベルを調整（必要に応じて）
    # uvicornやsqlalchemyのログは個別に制御可能


def get_logger(name: Optional[str] = None):
    """
    ロガーインスタンスを取得する
    
    Args:
        name: ロガー名（省略可能、loguruはグローバルロガーを使用）
        
    Returns:
        loguru.Logger: ロガーインスタンス
    """
    if name:
        return logger.bind(name=name)
    return logger

