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
            system_message = (
                "あなたは要件定義と設計を支援する専門家です。チャットではコード例を含めず、自然な日本語で説明してください。"
            )

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

    async def generate_document(self, doc_type: str) -> AsyncGenerator[str, None]:
        """
        要件定義書または設計書を生成します。

        Args:
            doc_type (str): ドキュメントタイプ（"requirements" または "design"）

        Yields:
            str: 生成されたドキュメントのチャンク
        """
        if doc_type == "requirements":
            system_message = (
                "あなたは要件定義のエキスパートです。"
                "これまでの会話を元に、マークダウン形式で要件定義書を作成してください。"
                "コード例は含めず、自然な日本語で記述してください。"
            )
            prompt = "これまでの会話を元に、要件定義書を作成してください。"
        elif doc_type == "design":
            system_message = (
                "あなたは技術設計のエキスパートです。"
                "これまでの会話を元に、マークダウン形式で設計書を作成してください。"
                "必要に応じてコード例やクラス図を含めて具体的に説明してください。"
            )
            prompt = "これまでの会話を元に、設計書を作成してください。"
        else:
            raise ValueError(f"無効なドキュメントタイプです: {doc_type}")

        async for chunk in self.process_message(prompt, system_message):
            yield chunk
