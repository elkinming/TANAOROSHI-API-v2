# Cursor でプロジェクトを実行するガイド

## クイックスタート

### 方法1: Cursor のデバッグ機能を使用する（推奨）

1. **依存関係をインストール**
   ```bash
   # VS のターミナルで実行
   pip install -r requirements.txt
   ```

2. **デバッグ設定を使用して実行**
   - `F5` キーを押すか、左側のデバッグボタンをクリック
   - "Python: FastAPI (Local)" 設定を選択
   - プロジェクトが自動的に起動し、ブレークポイントデバッグとホットリロードをサポート

### 方法2: ターミナルコマンドで実行する

1. **ターミナルを開く**
   - VS で `` Ctrl+` ``（バッククォート）を押して統合ターミナルを開く
   - またはメニューから：`Terminal` → `New Terminal`

2. **仮想環境を作成する（オプションだが推奨）**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **依存関係をインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **プロジェクトを実行**
   ```bash
   # local 環境を使用（デフォルト）
   # Windows では 127.0.0.1 を使用することを推奨（権限エラーを回避）
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
   
   # または環境を指定
   set ENVIRONMENT=local  # Windows
   # export ENVIRONMENT=local  # Linux/Mac
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
   ```

5. **アプリケーションにアクセス**
   - API ドキュメント：http://localhost:8080/docs
   - ReDoc：http://localhost:8080/redoc
   - ヘルスチェック：http://localhost:8080/health

## 環境設定

### デフォルト環境
- デフォルトで `local` 環境を使用
- 設定ファイル：`config.local.yaml`
- データベース接続情報は設定ファイルに設定済み

### 環境の切り替え
```bash
# Windows PowerShell
$env:ENVIRONMENT="dev"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

# Windows CMD
set ENVIRONMENT=dev
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

# Linux/Mac
export ENVIRONMENT=dev
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## デバッグのコツ

### ブレークポイントの設定
1. コード行番号の左側をクリックしてブレークポイントを設定（赤い丸）
2. `F5` キーでデバッグを開始
3. コードがブレークポイントに到達すると一時停止し、変数の値を確認できます

### ログの確認
- ローカル環境のログファイル：`logs/app.log`
- ログレベル：DEBUG（local 環境）

### ホットリロード
- `--reload` パラメータを使用すると、コード変更後に自動的に再起動されます
- 手動で停止・再起動する必要はありません

## よくある問題

### 1. WinError 10013 エラー（アクセス権限エラー）

Windows で `--host 0.0.0.0` を使用すると権限エラーが発生する場合があります。

**解決方法：**

**方法A: 127.0.0.1 を使用する（推奨）**
```bash
# ローカル開発では 127.0.0.1 で十分です
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

**方法B: 管理者権限で実行する**
- Cursor/VS Code を管理者として実行
- または PowerShell を管理者として実行してから起動

**方法C: ポートを変更する**
```bash
# 別のポートを使用
uvicorn app.main:app --reload --host 127.0.0.1 --port 8081
```

### 2. ポートが使用中
```bash
# Windows でポート使用状況を確認
netstat -ano | findstr :8080

# Linux/Mac でポート使用状況を確認
lsof -i :8080

# ポートを変更
uvicorn app.main:app --reload --host 127.0.0.1 --port 8081
```

### 3. 依存関係のインストールに失敗
```bash
# pip をアップグレード
python -m pip install --upgrade pip

# ミラーサイトを使用する（オプション）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. データベース接続に失敗
- `config.local.yaml` のデータベース接続情報を確認
- データベースサービスが実行されているか確認
- ネットワーク接続とファイアウォール設定を確認

## プロジェクト構造

```
backend/
├── app/
│   ├── main.py           # アプリケーションエントリーポイント
│   ├── config.py         # 設定管理
│   ├── database.py       # データベース接続
│   ├── api/              # API ルーター
│   ├── models/           # データモデル
│   ├── schemas/          # リクエスト/レスポンススキーマ
│   ├── services/         # ビジネスロジック
│   ├── repositories/     # データアクセス層
│   └── utils/            # ユーティリティ関数
├── config.yaml           # 共通設定
├── config.local.yaml     # ローカル環境設定
├── requirements.txt      # 依存関係リスト
└── .vscode/
    └── launch.json       # デバッグ設定
```

## 次のステップ

- [README.md](README.md) を確認してプロジェクトの詳細を理解する
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) を確認して開発ガイドラインを理解する
- http://localhost:8080/docs にアクセスして API ドキュメントを確認する
