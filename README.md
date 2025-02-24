# 要件定義書・設計書生成アシスタント

このプロジェクトは、チャットを通じて要件定義書と設計書を自動生成するアシスタントツールです。OpenAIのLLMを活用し、インタラクティブな対話を通じて文書を作成します。

## 機能

- OpenAIの複数モデル選択
  - chatgpt-4o-latest（デフォルト）
  - gpt-4
  - o1
  - o3-mini
- Gradioベースのチャットインターフェース
- ストリーミング出力対応
- 要件定義書・設計書の自動生成
- 生成したドキュメントのMarkdownファイルダウンロード

## セットアップ

1. 環境変数の設定:
```bash
# .env_sampleを.envにコピー
cp .env_sample .env

# .envを編集してOpenAI APIキーを設定
vim .env
```

2. 依存パッケージのインストール:
```bash
pip install -r requirements.txt
```

## 使い方

アプリケーションの起動:
```bash
python -m src.main
```

起動後、以下のURLでアクセス可能です：
- ローカル: http://0.0.0.0:7860
- パブリック: 起動時に表示されるURL

### 基本的な使い方

1. モデルの選択
   - 画面上部のドロップダウンから使用するモデルを選択

2. チャット
   - メッセージを入力して会話を進行
   - 通常の会話ではコード例は含まれません

3. ドキュメント生成
   - 「要件定義書を生成」ボタン：コード例を含まない要件定義書を生成
   - 「設計書を生成」ボタン：コード例を含む技術設計書を生成
   - 生成されたドキュメントはMarkdownファイルとしてダウンロード可能

### Dockerを使用する場合

開発環境をDockerで構築することもできます。

1. 開発環境の起動:
```bash
docker compose up -d
```

2. コンテナ内でコマンドを実行:
```bash
# コンテナのシェルにアクセス
docker compose exec app /bin/bash
```

3. 開発環境の停止:
```bash
docker compose down
```

## テスト

テストの実行:
```bash
pytest
```

### Dockerでのテスト実行

コンテナ内でテストを実行:
```bash
docker compose exec app pytest
```

## プロジェクト構成

```
.
├── docs/               # ドキュメント
│   ├── requirements.md # 要件定義書
│   └── design.md      # 設計書
├── src/               # ソースコード
│   ├── main.py       # エントリーポイント
│   ├── openai_client.py    # OpenAI API通信
│   ├── chat_controller.py  # チャット制御
│   └── gradio_interface.py # UI実装
├── tests/             # テストコード
├── .env_sample        # 環境変数設定例
└── requirements.txt   # 依存パッケージ
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
