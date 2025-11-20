# Tanaoroshi Backend API

RESTful API バックエンドサービス

## 技術スタック

- **Python**: 3.12
- **API フレームワーク**: FastAPI
- **データベースORM**: SQLModel
- **データベース**: PostgreSQL
- **ASGI サーバー**: Uvicorn

## クイックスタート

### Dockerを使用する場合

```bash
# イメージをビルド
docker build -t tanaoroshi-backend .

# コンテナを実行（開発環境）
docker run -p 8080:8080 \
  -e ENVIRONMENT=dev \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e LOG_LEVEL=INFO \
  tanaoroshi-backend

# APIは http://localhost:8080 でアクセス可能
```

### ローカル環境で実行する場合

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## プロジェクト構造

```
backend/
├── app/                    # アプリケーションコード
│   ├── main.py            # FastAPIアプリケーションエントリーポイント
│   ├── api/               # APIルーター
│   ├── models/            # SQLModelモデル定義
│   ├── schemas/           # Pydanticスキーマ定義
│   ├── services/          # ビジネスロジック層
│   ├── repositories/      # データアクセス層
│   └── utils/             # ユーティリティ関数
├── tests/                 # テストコード
├── requirements.txt       # 本番依存関係
├── requirements-dev.txt   # 開発依存関係
├── Dockerfile             # Dockerイメージ定義
└── pyproject.toml         # プロジェクト設定
```

## 環境設定

### 対応環境

プロジェクトは以下の4つの環境に対応しています：

- **local**: ローカル開発環境（ローカルマシン上での開発用）
- **dev**: AWS開発環境（AWSクラウド上）
- **staging**: AWSステージング環境（AWSクラウド上）
- **prod**: AWS本番環境（AWSクラウド上）

### 環境変数の設定

環境変数`ENVIRONMENT`を設定することで、環境に応じた設定ファイルが自動的に読み込まれます。

```bash
# ローカル開発環境
export ENVIRONMENT=local

# AWS開発環境
export ENVIRONMENT=dev

# AWSステージング環境
export ENVIRONMENT=staging

# AWS本番環境
export ENVIRONMENT=prod
```

### 設定ファイル

プロジェクトは**YAML形式**の設定ファイルを使用します。

**注意**: `.env`ファイルは使用しません。すべての設定はYAML設定ファイル（`config.yaml`）または環境変数で管理します。

プロジェクトルートに以下のYAML設定ファイルが用意されています：

- `config.yaml`: 共通設定ファイル
- `config.local.yaml`: ローカル開発環境用設定ファイル
- `config.dev.yaml`: AWS開発環境用設定ファイル
- `config.staging.yaml`: AWSステージング環境用設定ファイル
- `config.prod.yaml`: AWS本番環境用設定ファイル

各環境の設定ファイルを編集して、実際の値を設定してください。

**注意**: 設定ファイルは`.gitignore`で除外されているため、Gitにはコミットされません。機密情報（パスワード、シークレットキーなど）を含む設定は安全に管理してください。

### 主要な設定項目

YAML設定ファイルまたは環境変数で設定できます：

- `ENVIRONMENT`: 実行環境（local/dev/staging/prod）
- `database.url`: データベース接続URL（各環境の設定ファイルで設定、例: `postgresql://user:password@localhost:5432/dbname`）
- `log.level`: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `cors.origins`: CORS許可オリジン（YAMLではリスト形式、環境変数ではカンマ区切り）

**注意**: データベース設定は各環境の設定ファイル（`config.{environment}.yaml`）で設定します。共通設定ファイル（`config.yaml`）には含まれません。

詳細は [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) の「環境設定」セクションを参照してください。

## APIドキュメント

アプリケーション起動後、以下のURLでAPIドキュメントにアクセスできます：

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## 開発

詳細な開発ガイドラインは [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) を参照してください。

## ライセンス

MIT

