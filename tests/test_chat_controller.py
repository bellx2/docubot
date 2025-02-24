"""ChatControllerのテスト"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.chat_controller import ChatController


@pytest.fixture
def mock_openai_client():
    """OpenAIClientのモック"""
    client = MagicMock()
    client.DEFAULT_MODEL = "chatgpt-4o-latest"
    client.get_available_models.return_value = ["chatgpt-4o-latest", "gpt-4", "o1", "o3-mini"]
    return client


@pytest.fixture
def controller(mock_openai_client):
    """ChatControllerのフィクスチャ"""
    return ChatController(mock_openai_client)


def test_init(controller, mock_openai_client):
    """初期化時の状態を確認"""
    assert controller.client == mock_openai_client
    assert controller.history == []
    assert controller.current_model == mock_openai_client.DEFAULT_MODEL


def test_change_model_valid(controller):
    """有効なモデルに変更できることを確認"""
    controller.change_model("gpt-4")
    assert controller.current_model == "gpt-4"


def test_change_model_invalid(controller):
    """無効なモデルに変更できないことを確認"""
    with pytest.raises(ValueError):
        controller.change_model("invalid-model")


def test_update_history(controller):
    """履歴を更新できることを確認"""
    controller.update_history("user", "test message")
    assert controller.history == [{"role": "user", "content": "test message"}]

    controller.update_history("assistant", "test response")
    assert controller.history == [
        {"role": "user", "content": "test message"},
        {"role": "assistant", "content": "test response"},
    ]


def test_get_chat_history(controller):
    """チャット履歴をUI表示用の形式で取得できることを確認"""
    # 履歴がない場合
    assert controller.get_chat_history() == []

    # 履歴がある場合
    controller.update_history("user", "test message")
    controller.update_history("assistant", "test response")
    history = controller.get_chat_history()
    assert history == [("test message", "test response")]


@pytest.mark.asyncio
async def test_process_message(controller, mock_openai_client):
    """メッセージを処理してレスポンスを生成できることを確認"""
    # generate_streamのモック
    mock_openai_client.generate_stream = AsyncMock()

    async def mock_generate():
        yield "test "
        yield "response"

    mock_openai_client.generate_stream.return_value = mock_generate()

    # メッセージを処理
    response = ""
    async for chunk in controller.process_message("test message"):
        response += chunk

    # レスポンスを確認
    assert response == "test response"

    # 履歴が更新されていることを確認
    assert controller.history == [
        {"role": "user", "content": "test message"},
        {"role": "assistant", "content": "test response"},
    ]

    # APIが正しいパラメータで呼び出されたことを確認
    mock_openai_client.generate_stream.assert_called_once()
    call_args = mock_openai_client.generate_stream.call_args
    assert call_args[0][0] == controller.current_model  # モデル名
    assert len(call_args[0][1]) == 2  # メッセージ数（システム + ユーザー）
    assert call_args[0][1][0]["role"] == "system"  # システムメッセージ
    assert call_args[0][1][1] == {"role": "user", "content": "test message"}  # ユーザーメッセージ


@pytest.mark.asyncio
async def test_generate_document_requirements(controller, mock_openai_client):
    """要件定義書を生成できることを確認"""
    # generate_streamのモック
    mock_openai_client.generate_stream = AsyncMock()

    async def mock_generate():
        yield "要件定義書\n"
        yield "テスト"

    mock_openai_client.generate_stream.return_value = mock_generate()

    # ドキュメントを生成
    document = ""
    async for chunk in controller.generate_document("requirements"):
        document += chunk

    # 生成されたドキュメントを確認
    assert document == "要件定義書\nテスト"

    # APIが正しいパラメータで呼び出されたことを確認
    mock_openai_client.generate_stream.assert_called_once()
    call_args = mock_openai_client.generate_stream.call_args
    assert "要件定義書" in call_args[0][1][-1]["content"]


@pytest.mark.asyncio
async def test_generate_document_design(controller, mock_openai_client):
    """設計書を生成できることを確認"""
    # generate_streamのモック
    mock_openai_client.generate_stream = AsyncMock()

    async def mock_generate():
        yield "設計書\n"
        yield "テスト"

    mock_openai_client.generate_stream.return_value = mock_generate()

    # ドキュメントを生成
    document = ""
    async for chunk in controller.generate_document("design"):
        document += chunk

    # 生成されたドキュメントを確認
    assert document == "設計書\nテスト"

    # APIが正しいパラメータで呼び出されたことを確認
    mock_openai_client.generate_stream.assert_called_once()
    call_args = mock_openai_client.generate_stream.call_args
    assert "設計書" in call_args[0][1][-1]["content"]


@pytest.mark.asyncio
async def test_generate_document_invalid(controller):
    """無効なドキュメントタイプでエラーとなることを確認"""
    with pytest.raises(ValueError):
        async for _ in controller.generate_document("invalid"):
            pass
