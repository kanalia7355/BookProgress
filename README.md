# 読書管理アプリケーション

国会図書館APIを使用した読書進捗管理Webアプリケーション

## 機能

- ISBNコードから書籍情報を自動取得
- 読書時間の計測（開始・停止・リセット）
- 読書進捗の管理と可視化
- 複数書籍の同時管理
- 進捗バーによる視覚的な進捗表示

## 技術仕様

- **フロントエンド**: HTML5, CSS3, Vanilla JavaScript
- **バックエンド**: Python (Flask)
- **API**: 国会図書館API, OpenBD API
- **データ保存**: JSON ファイル

## セットアップ

### バックエンド

1. Pythonの仮想環境を作成
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

3. サーバーを起動
```bash
python app.py
```

### フロントエンド

1. ブラウザで `public/index.html` を開く
2. またはローカルサーバーを起動
```bash
cd public
python -m http.server 8000
```

## 使用方法

1. **書籍登録**: ISBNコードを入力して書籍を追加
2. **読書開始**: 「開始」ボタンで読書時間の計測を開始
3. **進捗更新**: 読んだページ数を入力して進捗を更新
4. **読書終了**: 「停止」ボタンで読書時間の計測を停止

## API エンドポイント

- `GET /api/book/{isbn}` - ISBN から書籍情報を取得
- `GET /api/books` - すべての書籍を取得
- `POST /api/books` - 書籍を保存
- `PUT /api/books/{id}` - 書籍情報を更新
- `DELETE /api/books/{id}` - 書籍を削除
- `GET /health` - ヘルスチェック

## ディレクトリ構造

```
BookProcess/
├── public/            # フロントエンド（静的ファイル）
│   ├── index.html
│   ├── css/
│   └── js/
├── api/               # Vercel サーバーレス関数
│   └── index.py
├── backend/           # バックエンド（開発用）
│   ├── app.py
│   ├── api/
│   └── models/
├── data/              # データファイル
└── README.md
```