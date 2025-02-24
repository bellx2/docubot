"""OpenAI APIとの通信を管理するモジュール"""

import os
from typing import AsyncGenerator, List, Dict
import openai
from openai import AsyncOpenAI


class OpenAIClient:
    """OpenAI APIとの通信を管理するクラス"""

    DEFAULT_MODEL = "chatgpt-4o-latest"
    AVAILABLE_MODELS = ["chatgpt-4o-latest", "gpt-4", "o1", "o3-mini"]

    def __init__(self, api_key: str = None):
        """
        OpenAIClientを初期化します。

        Args:
            api_key (str, optional): OpenAI APIキー。
                未指定の場合は環境変数OPENAI_API_KEYから読み込みます。
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI APIキーが設定されていません")

        self.client = AsyncOpenAI(api_key=self.api_key)

    def get_available_models(self) -> List[str]:
        """利用可能なモデル一覧を取得します。

        Returns:
            List[str]: 利用可能なモデルのリスト
        """
        return self.AVAILABLE_MODELS

    def _get_model_params(self, model: str) -> Dict:
        """モデル別のパラメータを設定します。

        Args:
            model (str): モデル名

        Returns:
            Dict: モデルパラメータ
        """
        # 基本パラメータ
        params = {
            "model": model,
            "temperature": 0,
            "stream": True,
        }

        # モデル別のパラメータ調整
        if model.startswith(("o1", "o3-")):
            params["max_completion_tokens"] = 4000
        else:
            params["max_tokens"] = 4000

        return params

    async def generate_stream(self, model: str, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """ストリーミング形式でレスポンスを生成します。

        Args:
            model (str): 使用するモデル名
            messages (List[Dict]): メッセージ履歴

        Yields:
            str: 生成されたテキスト

        Raises:
            openai.OpenAIError: API通信エラー
        """
        try:
            params = self._get_model_params(model)
            params["messages"] = messages

            async for chunk in await self.client.chat.completions.create(**params):
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except openai.OpenAIError as e:
            raise e
