# 設計書

## 1. システム概要設計

### 1.1 システムアーキテクチャ
```
[Gradio UI] <-> [Chat Controller] <-> [OpenAI API Client] <-> [OpenAI API]
```

### 1.2 主要コンポーネント
1. Gradio UI
   - チャットインターフェース
   - モデル選択ドロップダウン
   - ストリーミング出力表示
2. Chat Controller
   - 会話管理
   - 文書生成制御
3. OpenAI API Client
   - API通信制御
   - モデル別パラメータ管理

### 1.3 モデル設定
- デフォルトモデル: chatgpt-4o-latest
- 利用可能なモデル:
  - chatgpt-4o-latest
  - gpt-4
  - gpt-3.5-turbo
  - その他OpenAI APIで利用可能なモデル

## 2. 詳細設計

### 2.1 クラス設計

#### 2.1.1 OpenAIClient
```python
class OpenAIClient:
    """OpenAI APIとの通信を管理するクラス"""
    DEFAULT_MODEL = "chatgpt-4o-latest"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_available_models(self) -> List[str]:
        """利用可能なモデル一覧を取得"""
        
    async def generate_stream(self, model: str, messages: List[dict]) -> AsyncGenerator:
        """ストリーミング形式でレスポンスを生成"""
        
    def _get_model_params(self, model: str) -> dict:
        """モデル別のパラメータを設定"""
```

#### 2.1.2 ChatController
```python
class ChatController:
    """チャット制御とドキュメント生成を管理するクラス"""
    def __init__(self, openai_client: OpenAIClient):
        self.client = openai_client
        self.history = []
        self.current_model = openai_client.DEFAULT_MODEL
        
    async def process_message(self, message: str, model: str) -> AsyncGenerator:
        """メッセージを処理しレスポンスを生成"""
        
    def generate_document(self, doc_type: str) -> str:
        """要件定義書または設計書を生成"""
        
    def update_history(self, role: str, content: str):
        """会話履歴を更新"""
        
    def change_model(self, model: str):
        """使用するモデルを変更"""
```

#### 2.1.3 GradioInterface
```python
class GradioInterface:
    """Gradioインターフェースを管理するクラス"""
    def __init__(self, controller: ChatController):
        self.controller = controller
        
    def build_interface(self) -> gr.Interface:
        """Gradioインターフェースを構築"""
        with gr.Blocks() as interface:
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    choices=self.controller.client.get_available_models(),
                    value=self.controller.current_model,
                    label="モデルを選択"
                )
            # その他のUI要素
        
    async def chat_stream(self, message: str, model: str, history: List[List[str]]) -> Generator:
        """チャットストリームを処理"""
```

### 2.2 データフロー
1. ユーザーがメッセージを入力
2. GradioInterfaceがメッセージを受け取り、ChatControllerに転送
3. ChatControllerがOpenAIClientを使用してAPIリクエストを生成
4. OpenAIClientがストリーミングレスポンスを取得
5. レスポンスがGradioInterfaceを通じてユーザーに表示

### 2.3 エラーハンドリング
- API通信エラー
- モデル制限エラー
- 入力バリデーションエラー
- ストリーミング中断エラー

## 3. インターフェース設計

### 3.1 Gradio UI構成
- モデル選択ドロップダウン（上部に配置）
  - デフォルト値: chatgpt-4o-latest
  - 動的に利用可能なモデルをリスト表示
- チャット履歴表示エリア
- メッセージ入力エリア
- 文書生成ボタン
- 生成文書表示・編集エリア

### 3.2 API通信
- OpenAI APIとの通信プロトコル
- ストリーミングレスポンスの処理
- エラーレスポンスのハンドリング

## 4. セキュリティ設計
- API認証情報の環境変数管理
- 入力データのサニタイズ
- エラーメッセージのセキュアな表示

## 5. テスト設計
- ユニットテスト
  - OpenAIClient
    - モデル一覧取得
    - パラメータ設定
  - ChatController
    - モデル切り替え
    - メッセージ処理
  - GradioInterface
    - UIコンポーネント
    - イベントハンドリング
- 統合テスト
  - エンドツーエンドのチャットフロー
  - 文書生成フロー
  - モデル切り替えフロー
- エラーケーステスト
  - API通信エラー
  - 入力バリデーション
  - ストリーミング中断

## 6. 開発環境・依存関係
- Python 3.8+
- Gradio
- OpenAI Python SDK
- pytest（テスト用）
- python-dotenv（環境変数管理）