"""OpenAIClientのテスト"""

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.openai_client import OpenAIClient


@pytest.fixture
def client():
    """OpenAIClientのフィクスチャ"""
    os.environ["OPENAI_API_KEY"] = "test-api-key"
    return OpenAIClient()


def test_init_with_api_key():
    """APIキーを指定して初期化できることを確認"""
    client = OpenAIClient(api_key="test-key")
    assert client.api_key == "test-key"


def test_init_with_env_var(client):
    """環境変数からAPIキーを読み込めることを確認"""
    assert client.api_key == "test-api-key"


def test_init_without_api_key():
    """APIキーが未設定の場合にエラーとなることを確認"""
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    with pytest.raises(ValueError):
        OpenAIClient()


def test_get_available_models(client):
    """利用可能なモデル一覧を取得できることを確認"""
    models = client.get_available_models()
    assert isinstance(models, list)
    assert "chatgpt-4o-latest" in models
    assert "gpt-4" in models
    assert "o1" in models
    assert "o3-mini" in models


def test_get_model_params(client):
    """モデル別のパラメータを正しく設定できることを確認"""
    # o1モデルのパラメータ
    o1_params = client._get_model_params("o1")
    assert o1_params["model"] == "o1"
    assert o1_params["max_completion_tokens"] == 4000
    assert o1_params["temperature"] == 0
    assert o1_params["stream"] is True

    # o3-miniモデルのパラメータ
    o3_params = client._get_model_params("o3-mini")
    assert o3_params["model"] == "o3-mini"
    assert o3_params["max_completion_tokens"] == 4000
    assert o3_params["temperature"] == 0
    assert o3_params["stream"] is True

    # gpt-4モデルのパラメータ
    gpt4_params = client._get_model_params("gpt-4")
    assert gpt4_params["model"] == "gpt-4"
    assert gpt4_params["max_tokens"] == 4000
    assert gpt4_params["temperature"] == 0
    assert gpt4_params["stream"] is True


@pytest.mark.asyncio
async def test_generate_stream(client):
    """ストリーミングレスポンスを生成できることを確認"""
    # AsyncOpenAIのモック
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.choices = [MagicMock(delta=MagicMock(content="test response"))]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch.object(client, "client", mock_client):
        messages = [{"role": "user", "content": "test message"}]
        async for chunk in client.generate_stream("gpt-4", messages):
            assert chunk == "test response"

        # APIが正しいパラメータで呼び出されたことを確認
        call_args = mock_client.chat.completions.create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert call_args["messages"] == messages
        assert call_args["stream"] is True


@pytest.mark.asyncio
async def test_generate_stream_error(client):
    """APIエラー時に例外が伝播することを確認"""
    from openai import OpenAIError

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=OpenAIError("API Error"))

    with patch.object(client, "client", mock_client):
        messages = [{"role": "user", "content": "test message"}]
        with pytest.raises(OpenAIError):
            async for _ in client.generate_stream("gpt-4", messages):
                pass
