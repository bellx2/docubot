"""チャット制御とドキュメント生成を管理するモジュール"""

from typing import AsyncGenerator, List, Dict, Tuple
from .openai_client import OpenAIClient


class ChatController:
    """チャット制御とドキュメント生成を管理するクラス"""

    def __init__(self, openai_client: OpenAIClient):
        """
        ChatControllerを初期化します。

        Args:
            openai_client (OpenAIClient): OpenAIクライアントインスタンス
        """
        self.client = openai_client
        self.history: List[Dict[str, str]] = []
        self.current_model = openai_client.DEFAULT_MODEL

    def change_model(self, model: str) -> None:
        """
        使用するモデルを変更します。

        Args:
            model (str): 新しいモデル名
        """
        if model not in self.client.get_available_models():
            raise ValueError(f"無効なモデル名です: {model}")
        self.current_model = model

    def update_history(self, role: str, content: str) -> None:
        """
        会話履歴を更新します。

        Args:
            role (str): メッセージの役割（"user" または "assistant"）
            content (str): メッセージの内容
        """
        self.history.append({"role": role, "content": content})

    def get_chat_history(self) -> List[Tuple[str, str]]:
        """
        チャット履歴をUI表示用の形式で取得します。

        Returns:
            List[Tuple[str, str]]: (ユーザーメッセージ, アシスタントメッセージ)のリスト
        """
        # Gradio用に履歴を整形
        formatted_history = []
        for i in range(0, len(self.history), 2):
            if i + 1 < len(self.history):
                user_msg = self.history[i]["content"]
                assistant_msg = self.history[i + 1]["content"]
                formatted_history.append((user_msg, assistant_msg))
        return formatted_history

    async def generate_initial_message(self) -> str:
        """
        初期メッセージをLLMを使って動的に生成します。

        Returns:
            str: 生成された初期メッセージ
        """
        system_message = """あなたは要件定義と設計を支援する専門家です。これから新しいユーザーとの会話を始めます。
ユーザーがどのようなプロジェクトを開発したいのか尋ねる最初のメッセージを生成してください。
メッセージは親しみやすく、自然な日本語で、毎回異なる表現を使って質問してください。
ユーザーの開発したいシステムやアプリケーションの目的、ビジョン、機能などについて質問するメッセージを作成してください。"""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": "新しいユーザーとの会話を始めるための最初のメッセージを生成してください。"},
        ]

        initial_message = ""
        async for chunk in self.client.generate_stream(self.current_model, messages):
            initial_message += chunk

        return initial_message

    async def process_message(self, message: str, system_message: str = None) -> AsyncGenerator[str, None]:
        """
        メッセージを処理しレスポンスを生成します。

        Args:
            message (str): ユーザーメッセージ
            system_message (str, optional): システムメッセージ。
                未指定の場合はデフォルトのメッセージを使用。

        Yields:
            str: 生成されたレスポンス
        """
        # システムメッセージを設定
        if system_message is None:
            system_message = """あなたは要件定義と設計を支援する専門家です。チャットではコード例を含めず、自然な日本語で説明してください。"""

        messages = [{"role": "system", "content": system_message}]
        # 履歴を追加
        messages.extend(self.history)
        # 新しいメッセージを追加
        messages.append({"role": "user", "content": message})

        # ユーザーメッセージを履歴に追加
        self.update_history("user", message)

        # レスポンスを生成
        response_text = ""
        async for chunk in self.client.generate_stream(self.current_model, messages):
            response_text += chunk
            yield chunk

        # アシスタントの応答を履歴に追加
        self.update_history("assistant", response_text)

    async def generate_document(self, doc_type: str = None) -> AsyncGenerator[str, None]:
        """
        要件定義と設計書を統合した文書を生成します。

        Args:
            doc_type (str, optional): 後方互換性のために残していますが、使用されません。

        Yields:
            str: 生成されたドキュメントのチャンク
        """
        # Few-shotのサンプルとして、design.mdを読み込む
        import os

        design_md_path = os.path.join("docs", "design.md")
        design_md_content = ""

        try:
            if os.path.exists(design_md_path):
                with open(design_md_path, "r", encoding="utf-8") as f:
                    design_md_content = f.read()
        except Exception as e:
            print(f"サンプルファイル読み込みエラー: {e}")

        system_message = f"""あなたは要件定義と設計のエキスパートです。
これまでの会話を元に、マークダウン形式で要件と設計を統合した文書を作成してください。

要件定義と設計を別々の章として含め、以下の構成に従ってください：
1. 要件定義：プロジェクト概要、機能要件、非機能要件、制約条件など
2. システム設計：システム概要設計、詳細設計、インターフェース設計、セキュリティ設計、テスト設計、開発環境・依存関係、開発工程

以下のサンプルを参考にしてください：

{design_md_content}

上記のサンプルと同様のフォーマットで、要件・設計書を作成してください。但し、内容は現在のプロジェクトに合わせて変更してください。
"""

        prompt = "これまでの会話を元に、要件・設計書を作成してください。"

        async for chunk in self.process_message(prompt, system_message):
            yield chunk
