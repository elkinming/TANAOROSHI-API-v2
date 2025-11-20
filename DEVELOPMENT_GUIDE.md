# 開発ガイドライン

## 環境要件

- **Python バージョン**: 3.12以上
- **実行環境**: Python 3.12

## 依存関係のインストール

### 本番環境

```bash
pip install -r requirements.txt
```

### 開発環境

```bash
pip install -r requirements-dev.txt
```

または、個別にインストールする場合:

```bash
# 本番依存関係をインストール
pip install -r requirements.txt

# 開発依存関係を追加インストール
pip install -r requirements-dev.txt
```

## 環境設定

### 対応環境

プロジェクトは以下の4つの環境に対応しています：

- **local**: ローカル開発環境（ローカルマシン上での開発用）
- **dev**: AWS開発環境（AWSクラウド上）
- **staging**: AWSステージング環境（AWSクラウド上）
- **prod**: AWS本番環境（AWSクラウド上）

### 設定ファイル形式

プロジェクトは**YAML形式**の設定ファイルを使用します。

**注意**: `.env`ファイルは使用しません。すべての設定はYAML設定ファイル（`config.yaml`）または環境変数で管理します。

### 環境変数の設定

環境変数`ENVIRONMENT`を設定することで、環境に応じた設定ファイル（`config.local.yaml`, `config.dev.yaml`, `config.staging.yaml`, `config.prod.yaml`）が自動的に読み込まれます。

#### ローカル開発環境

```bash
# 環境変数を設定
export ENVIRONMENT=local

# config.local.yamlファイルを編集して設定値を変更

# アプリケーションを起動
uvicorn app.main:app --reload
```

#### AWS開発環境

```bash
# 環境変数を設定
export ENVIRONMENT=dev

# config.dev.yamlファイルを編集して設定値を変更

# アプリケーションを起動
uvicorn app.main:app --reload
```

#### AWSステージング環境

```bash
# 環境変数を設定
export ENVIRONMENT=staging

# config.staging.yamlファイルを編集して設定値を変更

# アプリケーションを起動
uvicorn app.main:app
```

#### AWS本番環境

```bash
# 環境変数を設定
export ENVIRONMENT=prod

# config.prod.yamlファイルを編集して設定値を変更（特にDATABASE_URL）

# アプリケーションを起動
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 設定ファイルの使い分け

- **`config.yaml`**: 全環境で共通の設定を記述します
- **`config.{environment}.yaml`**: 環境ごとに異なる設定のみを記述します

**設定のマージ順序**:
1. `config.yaml`（共通設定）を読み込む
2. `config.{environment}.yaml`（環境固有設定）を読み込んで上書き

**重要な注意事項**:
- **データベース設定**は各環境で異なるため、`config.yaml`には含めず、各環境の設定ファイル（`config.{environment}.yaml`）でのみ設定します。

**例**:
- `config.yaml`に`api.title: "Tanaoroshi Backend API"`を記述
- `config.dev.yaml`に`api.title: "Tanaoroshi Backend API (Dev)"`と`database.url: "postgresql://..."`を記述
- 結果: 開発環境では`api.title`が`"Tanaoroshi Backend API (Dev)"`になり、`database.url`が環境固有の値になります

### 設定の優先順位

1. **環境変数**（システム環境変数）- 最優先
2. **YAML設定ファイル**（`config.{environment}.yaml` - 環境固有設定）
3. **基本設定ファイル**（`config.yaml` - 共通設定）
4. **デフォルト値**

### 設定ファイル

プロジェクトルートに以下のYAML設定ファイルが用意されています：

- `config.yaml`: 共通設定ファイル
- `config.local.yaml`: ローカル開発環境用設定ファイル
- `config.dev.yaml`: AWS開発環境用設定ファイル
- `config.staging.yaml`: AWSステージング環境用設定ファイル
- `config.prod.yaml`: AWS本番環境用設定ファイル

各環境の設定ファイルを編集して、実際の値を設定してください。

**注意**: 設定ファイルは`.gitignore`で除外されているため、Gitにはコミットされません。機密情報（パスワード、シークレットキーなど）を含む設定は安全に管理してください。

### YAML設定ファイルの構造

設定ファイルは階層構造で記述できます：

```yaml
# config.dev.yamlの例
environment: dev

api:
  title: "Tanaoroshi Backend API (Dev)"
  debug: true

database:
  url: "postgresql://postgres:postgres@localhost:5432/tanaoroshi_dev"
  echo: true

log:
  level: "DEBUG"

cors:
  origins:
    - "*"
  allow_methods:
    - "*"
```

### 設定項目

主要な設定項目（YAML形式）：

```yaml
environment: dev  # 実行環境（dev/staging/prod）

api:
  title: "APIタイトル"
  version: "0.1.0"
  debug: true  # デバッグモード

server:
  host: "0.0.0.0"
  port: 8080

# データベース設定は各環境の設定ファイル（config.{environment}.yaml）で設定します
# database:
#   url: "postgresql://user:password@host:5432/dbname"
#   echo: false

log:
  level: "DEBUG"  # DEBUG/INFO/WARNING/ERROR/CRITICAL
  file: null  # ログファイルパス（nullの場合は標準出力のみ）

cors:
  origins:  # CORS許可オリジン（リスト形式）
    - "*"
  allow_methods:  # 許可するHTTPメソッド
    - "*"
  allow_headers:  # 許可するHTTPヘッダー
    - "*"

```

### 設定の使用例

```python
from app.config import settings

# 設定値にアクセス
print(settings.database_url)
print(settings.log_level)

# 環境判定
if settings.is_dev:
    print("開発環境です")
elif settings.is_prod:
    print("本番環境です")

# CORS設定をリスト形式で取得
cors_origins = settings.get_cors_origins_list()
```

### Dockerでの環境設定

```bash
# 開発環境
docker run -p 8080:8080 \
  -e ENVIRONMENT=dev \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  tanaoroshi-backend

# 本番環境
docker run -p 8080:8080 \
  -e ENVIRONMENT=prod \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  tanaoroshi-backend
```

## Dockerでの実行

### 前提条件

- Docker Engine 20.10以上

### Dockerコマンド

```bash
# イメージをビルド
docker build -t tanaoroshi-backend .

# コンテナを実行（環境変数を設定）
docker run -p 8080:8080 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e LOG_LEVEL=INFO \
  tanaoroshi-backend

# バックグラウンドで実行
docker run -d -p 8080:8080 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e LOG_LEVEL=INFO \
  --name tanaoroshi-api \
  tanaoroshi-backend

# ログを確認
docker logs -f tanaoroshi-api

# コンテナを停止
docker stop tanaoroshi-api

# コンテナを削除
docker rm tanaoroshi-api

# コンテナ内でシェルを実行
docker exec -it tanaoroshi-api bash
```

### ヘルスチェック

アプリケーションのヘルスチェックエンドポイント:
```bash
curl http://localhost:8080/health
```

## プロジェクト構成

### 技術スタック

- **API フレームワーク**: FastAPI
- **データベースORM**: SQLModel
- **ASGI サーバー**: Uvicorn

### プロジェクト構造

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリケーションエントリーポイント
│   ├── config.py            # 設定管理
│   ├── database.py          # データベース接続設定
│   ├── models/              # SQLModelモデル定義
│   │   ├── __init__.py
│   │   └── *.py
│   ├── schemas/             # Pydanticスキーマ定義
│   │   ├── __init__.py
│   │   └── *.py
│   ├── api/                 # APIルーター
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       └── *.py
│   ├── services/            # ビジネスロジック層
│   │   ├── __init__.py
│   │   └── *.py
│   ├── repositories/        # データアクセス層
│   │   ├── __init__.py
│   │   └── *.py
│   └── utils/              # ユーティリティ関数
│       ├── __init__.py
│       └── logger.py       # ログ設定
├── tests/                   # テストコード
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── pyproject.toml          # プロジェクト設定
├── .editorconfig           # エディタ設定
└── README.md
```

## コーディング規約

### 1. コメント

- **すべてのコメントは日本語で記述する**
- 関数・クラスにはdocstringを記述する
- 複雑なロジックには説明コメントを追加する

```python
def get_user_by_id(user_id: int) -> User:
    """
    ユーザーIDからユーザー情報を取得する
    
    Args:
        user_id: ユーザーID
        
    Returns:
        User: ユーザーオブジェクト
        
    Raises:
        NotFoundError: ユーザーが見つからない場合
    """
    # データベースからユーザー情報を取得
    user = session.get(User, user_id)
    if not user:
        raise NotFoundError(f"ユーザーID {user_id} が見つかりません")
    return user
```

### 2. ログ出力

プロジェクトは**Loguru**を使用してログ出力を行います。Loguruは標準の`logging`モジュールよりも使いやすく、以下の機能を提供します：

- **自動ローテーション**: サイズまたは日付ベースの自動ログローテーション
- **色付き出力**: コンソールでの色付きログ出力
- **例外トレースバック**: 自動的な例外の詳細なトレースバック
- **構造化ログ**: JSON形式でのログ出力も可能
- **非同期ログ**: パフォーマンス向上のための非同期ログ

- **ログレベルに応じて適切に出力する**
- 以下のログレベルを使用する:
  - `DEBUG`: デバッグ情報（開発時のみ）
  - `INFO`: 一般的な情報（リクエスト処理開始・終了など）
  - `WARNING`: 警告（非致命的な問題）
  - `ERROR`: エラー（処理失敗）
  - `CRITICAL`: 致命的なエラー

```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

def process_request(request_data: dict):
    logger.info(f"リクエスト処理開始: {request_data}")
    try:
        # 処理ロジック
        logger.debug("詳細なデバッグ情報")
        result = perform_operation(request_data)
        logger.info(f"処理成功: {result}")
        return result
    except ValueError as e:
        logger.warning(f"値エラー: {e}")
        raise
    except Exception as e:
        logger.error(f"処理エラー: {e}")  # exc_infoは自動的に含まれる
        raise
```

### 3. モジュール化

- **関心の分離**: 各モジュールは単一の責任を持つ
- **レイヤー分離**:
  - `api/`: HTTPリクエスト/レスポンス処理
  - `services/`: ビジネスロジック
  - `repositories/`: データアクセス
  - `models/`: データモデル定義
  - `schemas/`: APIスキーマ定義

### 4. 命名規則

- **ファイル名**: スネークケース（`user_service.py`）
- **クラス名**: パスカルケース（`UserService`）
- **関数・変数名**: スネークケース（`get_user_by_id`）
- **定数**: 大文字スネークケース（`MAX_RETRY_COUNT`）

### 5. 型ヒント

- **すべての関数に型ヒントを記述する**
- 戻り値の型も明示する

```python
from typing import Optional, List

def find_users(
    name: Optional[str] = None,
    limit: int = 10
) -> List[User]:
    """ユーザー検索"""
    pass
```

### 6. エラーハンドリング

- **適切な例外処理を実装する**
- FastAPIのHTTPExceptionを使用してHTTPエラーを返す

```python
from fastapi import HTTPException, status

def get_user(user_id: int) -> User:
    user = repository.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ユーザーID {user_id} が見つかりません"
        )
    return user
```

## データベース設定

### SQLModelの使用

- SQLModelを使用してモデル定義とデータベース操作を行う
- モデルは`app/models/`ディレクトリに配置する

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    created_at: datetime = Field(default_factory=datetime.now)
```

## API設計

### RESTful原則

- **リソース指向**: URLは名詞を使用（`/users`, `/orders`）
- **HTTPメソッド**: GET（取得）、POST（作成）、PUT（更新）、DELETE（削除）
- **ステータスコード**: 適切なHTTPステータスコードを返す

### エンドポイント例

```python
from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends()
):
    """ユーザー作成"""
    return await service.create_user(user_data)
```

## ログ設定

### ログレベル設定

環境変数または設定ファイルでログレベルを制御する:

```python
from app.utils.logger import setup_logging, get_logger
from app.config import settings

# ログ設定を初期化
setup_logging(
    log_level=settings.log_level,
    log_file=settings.log_file,
    max_bytes=settings.log_max_bytes,
    backup_count=settings.log_backup_count,
    when=settings.log_when
)

# ロガーを使用
logger = get_logger(__name__)
logger.info("アプリケーション起動")
logger.debug("デバッグ情報")
logger.error("エラー発生", exc_info=True)  # 例外情報も自動的に記録
```

## テスト

- **単体テスト**: 各関数・メソッドのテスト
- **統合テスト**: APIエンドポイントのテスト
- **テストカバレッジ**: 可能な限り高いカバレッジを目指す

## コード品質ツール

- **Black**: コードフォーマッター
- **Ruff**: リンター
- **mypy**: 型チェッカー

これらのツールは`pyproject.toml`で設定済みです。

## 開発フロー

1. 機能ブランチを作成
2. コードを実装（コメントは日本語）
3. テストを記述・実行
4. コードフォーマット・リンター実行
5. プルリクエスト作成

