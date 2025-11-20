"""
設定管理モジュール

YAML設定ファイルと環境変数から設定を読み込み、dev、staging、prodの3つの環境に対応する
"""
import os
from enum import Enum
from pathlib import Path
from typing import Optional, Any
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """実行環境の列挙型"""
    LOCAL = "local"  # ローカル開発環境
    DEV = "dev"  # AWS開発環境
    STAGING = "staging"  # AWSステージング環境
    PROD = "prod"  # AWS本番環境


def load_yaml_config(config_path: Path) -> dict[str, Any]:
    """
    YAML設定ファイルを読み込む
    
    Args:
        config_path: YAMLファイルのパス
        
    Returns:
        dict[str, Any]: 設定値の辞書（ファイルが存在しない場合は空の辞書）
    """
    if config_path.exists() and config_path.is_file():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def get_config_files() -> list[Path]:
    """
    環境変数ENVIRONMENTに基づいて設定ファイルのパスリストを取得する
    
    読み込み順序:
    1. config.yaml - 共通設定（全環境で共通の設定）
    2. config.{environment}.yaml - 環境固有設定（環境ごとに異なる設定）
    
    マージ時は環境固有設定が共通設定を上書きします。
    
    Returns:
        list[Path]: 設定ファイルのパスリスト
    """
    env = os.getenv("ENVIRONMENT", "local").lower()
    config_files = []
    
    # まず共通設定ファイルを読み込む
    config_files.append(Path("config.yaml"))
    
    # 次に環境固有の設定ファイルを読み込む（共通設定を上書き）
    if env in ["local", "dev", "staging", "prod"]:
        config_files.append(Path(f"config.{env}.yaml"))
    
    return config_files


def load_all_configs() -> dict[str, Any]:
    """
    すべての設定ファイルを読み込んでマージする
    
    読み込み順序:
    1. config.yaml（共通設定）を読み込む
    2. config.{environment}.yaml（環境固有設定）を読み込んで上書き
    
    マージ結果: 環境固有設定が共通設定を上書きします。
    
    Returns:
        dict[str, Any]: マージされた設定値の辞書
    """
    config_files = get_config_files()
    merged_config = {}
    
    # 順番に読み込んでマージ（後から読み込んだ設定が優先される）
    for config_file in config_files:
        file_config = load_yaml_config(config_file)
        # ネストされた辞書を深くマージ
        merged_config = _deep_merge(merged_config, file_config)
    
    return merged_config


def _deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """
    2つの辞書を深くマージする
    
    Args:
        base: ベースとなる辞書
        update: 更新する辞書
        
    Returns:
        dict[str, Any]: マージされた辞書
    """
    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def flatten_config(config: dict[str, Any], parent_key: str = "", sep: str = "_") -> dict[str, Any]:
    """
    ネストされた辞書をフラット化する
    
    YAML設定ファイルのネスト構造をPydantic Settingsのフィールド名に変換する
    
    Args:
        config: ネストされた設定辞書
        parent_key: 親キー（再帰呼び出し用）
        sep: キーの区切り文字
        
    Returns:
        dict[str, Any]: フラット化された辞書
    """
    items = []
    for key, value in config.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_config(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


class Settings(BaseSettings):
    """
    アプリケーション設定クラス
    
    環境変数から設定値を読み込む
    """
    
    # 実行環境
    environment: Environment = Environment.LOCAL
    
    # API設定
    api_title: str = "Tanaoroshi Backend API"
    api_version: str = "0.1.0"
    api_description: str = "RESTful API バックエンドサービス"
    debug: bool = False
    api_root_path: Optional[str] = None  # FastAPIのroot_pathパラメータ
    
    # サーバー設定
    host: str = "0.0.0.0"
    port: int = 8080
    
    # データベース設定
    database_url: str = ""
    database_echo: bool = False  # SQLAlchemyのSQLログ出力
    database_pool_pre_ping: bool = True  # 接続の有効性を確認
    database_pool_size: int = 10  # 接続プールサイズ
    database_max_overflow: int = 20  # 最大オーバーフロー
    
    # ログ設定
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_max_bytes: Optional[int] = None  # ログファイルの最大サイズ（バイト）、Noneの場合はサイズローテーション無効
    log_backup_count: int = 5  # 保持するバックアップファイル数
    log_when: Optional[str] = None  # 日付ベースローテーション間隔（'D'=日次、'H'=時間、'midnight'=日次深夜）
    
    # CORS設定（カンマ区切りの文字列として受け取り、リストに変換）
    cors_origins: str = "*"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"
    
    # その他の設定
    project_name: str = "tanaoroshi-backend"
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        """
        設定を初期化し、環境に応じた設定を適用する
        
        YAML設定ファイルと環境変数の両方から設定を読み込む
        優先順位: 環境変数 > YAML設定ファイル > デフォルト値
        
        Args:
            **kwargs: 設定値のキーワード引数
        """
        # YAML設定ファイルから設定を読み込む
        yaml_config = load_all_configs()
        
        # ネストされた構造をフラット化
        flattened_config = flatten_config(yaml_config)
        
        # YAML設定をkwargsにマージ（kwargsが優先）
        merged_kwargs = {**flattened_config, **kwargs}
        
        # 環境変数から環境を取得（環境変数が最優先）
        env_str = os.getenv("ENVIRONMENT", merged_kwargs.get("environment", "local")).lower()
        merged_kwargs["environment"] = env_str
        
        # CORS設定を文字列に変換（リストの場合はカンマ区切り文字列に変換）
        # Pydanticの検証前に変換する必要がある
        if "cors_origins" in merged_kwargs and isinstance(merged_kwargs["cors_origins"], list):
            if len(merged_kwargs["cors_origins"]) == 1 and merged_kwargs["cors_origins"][0] == "*":
                merged_kwargs["cors_origins"] = "*"
            else:
                merged_kwargs["cors_origins"] = ",".join(merged_kwargs["cors_origins"])
        
        if "cors_allow_methods" in merged_kwargs and isinstance(merged_kwargs["cors_allow_methods"], list):
            if len(merged_kwargs["cors_allow_methods"]) == 1 and merged_kwargs["cors_allow_methods"][0] == "*":
                merged_kwargs["cors_allow_methods"] = "*"
            else:
                merged_kwargs["cors_allow_methods"] = ",".join(merged_kwargs["cors_allow_methods"])
        
        if "cors_allow_headers" in merged_kwargs and isinstance(merged_kwargs["cors_allow_headers"], list):
            if len(merged_kwargs["cors_allow_headers"]) == 1 and merged_kwargs["cors_allow_headers"][0] == "*":
                merged_kwargs["cors_allow_headers"] = "*"
            else:
                merged_kwargs["cors_allow_headers"] = ",".join(merged_kwargs["cors_allow_headers"])
        
        super().__init__(**merged_kwargs)
        
        # 環境を設定
        try:
            self.environment = Environment(env_str)
        except ValueError:
            self.environment = Environment.LOCAL
        
        # 環境に応じたデフォルト値を設定
        if self.environment == Environment.LOCAL:
            # ローカル開発環境: デバッグモード有効、詳細ログ出力
            if not merged_kwargs.get("debug"):
                self.debug = True
            if not merged_kwargs.get("log_level"):
                self.log_level = "DEBUG"
            if not merged_kwargs.get("database_echo"):
                self.database_echo = True
        elif self.environment == Environment.DEV:
            # AWS開発環境: デバッグモード有効、詳細ログ出力
            if not merged_kwargs.get("debug"):
                self.debug = True
            if not merged_kwargs.get("log_level"):
                self.log_level = "DEBUG"
            if not merged_kwargs.get("database_echo"):
                self.database_echo = True
        elif self.environment == Environment.STAGING:
            # AWSステージング環境: 本番に近い設定
            self.debug = False
            if not merged_kwargs.get("log_level"):
                self.log_level = "INFO"
            self.database_echo = False
        elif self.environment == Environment.PROD:
            # AWS本番環境: 本番設定
            self.debug = False
            if not merged_kwargs.get("log_level"):
                self.log_level = "INFO"
            self.database_echo = False
    
    def get_cors_origins_list(self) -> list[str]:
        """
        CORSオリジンをリスト形式で取得する
        
        Returns:
            list[str]: CORSオリジンのリスト
        """
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def get_cors_methods_list(self) -> list[str]:
        """
        CORSメソッドをリスト形式で取得する
        
        Returns:
            list[str]: CORSメソッドのリスト
        """
        if self.cors_allow_methods == "*":
            return ["*"]
        return [method.strip() for method in self.cors_allow_methods.split(",")]
    
    def get_cors_headers_list(self) -> list[str]:
        """
        CORSヘッダーをリスト形式で取得する
        
        Returns:
            list[str]: CORSヘッダーのリスト
        """
        if self.cors_allow_headers == "*":
            return ["*"]
        return [header.strip() for header in self.cors_allow_headers.split(",")]
    
    @property
    def is_local(self) -> bool:
        """ローカル開発環境かどうかを判定"""
        return self.environment == Environment.LOCAL
    
    @property
    def is_dev(self) -> bool:
        """AWS開発環境かどうかを判定"""
        return self.environment == Environment.DEV
    
    @property
    def is_staging(self) -> bool:
        """AWSステージング環境かどうかを判定"""
        return self.environment == Environment.STAGING
    
    @property
    def is_prod(self) -> bool:
        """AWS本番環境かどうかを判定"""
        return self.environment == Environment.PROD


# グローバル設定インスタンス
settings = Settings()

