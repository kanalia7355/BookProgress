# プロジェクト構造

## ディレクトリ構成

```
BookProcess/
├── public/                 # Vercel静的ファイル
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js
│   │   ├── book.js
│   │   └── timer.js
│   └── assets/
│       └── images/
├── api/                    # Vercelサーバーレス関数
│   └── index.py
├── backend/                # 開発用（ローカル）
│   ├── app.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── ndl_api.py
│   │   └── book_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── book_model.py
│   └── requirements.txt
├── data/
│   └── books.json
├── README.md
└── CLAUDE.md
```

## 技術スタック

- **フロントエンド**: HTML5, CSS3, Vanilla JavaScript
- **バックエンド**: Python (Flask)
- **API**: 国会図書館API
- **データ保存**: JSON ファイル（後にデータベースに拡張可能）