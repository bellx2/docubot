"""GradioInterfaceのテスト"""

import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import gradio as gr
from src.gradio_interface import GradioInterface


@pytest.fixture
def mock_controller():
    """ChatControllerのモック"""
    controller = MagicMock()
    controller.current_model = "chatgpt-4o-latest"
    controller.client.get_available_models.return_value = ["chatgpt-4o-latest", "gpt-4", "o1", "o3-mini"]
    return controller


@pytest.fixture
def interface(mock_controller):
    """GradioInterfaceのフィクスチャ"""
    return GradioInterface(mock_controller)


def test_init(interface, mock_controller):
    """初期化時の状態を確認"""
    assert interface.controller == mock_controller
    assert isinstance(interface.temp_dir, Path)


@pytest.mark.asyncio
async def test_chat_stream(interface, mock_controller):
    """チャットストリームを処理できることを確認"""
    # process_messageのモック
    mock_controller.process_message = AsyncMock()

    async def mock_process():
        yield "test "
        yield "response"

    mock_controller.process_message.return_value = mock_process()

    # チャットストリームを処理
    history = []
    message = "test message"
    model = "gpt-4"

    async for empty_str, new_history in interface.chat_stream(message, history, model):
        # 空文字列が返されることを確認（Gradioの仕様）
        assert empty_str == ""
        # 履歴が正しく更新されることを確認
        assert len(new_history) == 1
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == message

    # モデルが変更された場合、change_modelが呼ばれることを確認
    mock_controller.change_model.assert_called_once_with(model)


@pytest.mark.asyncio
async def test_generate_doc_stream(interface, mock_controller):
    """ドキュメントをストリーミング生成できることを確認"""
    # generate_documentのモック
    mock_controller.generate_document = AsyncMock()

    async def mock_generate():
        yield "要件定義書\n"
        yield "テスト"

    mock_controller.generate_document.return_value = mock_generate()

    # ドキュメントを生成
    history = []
    doc_type = "requirements"

    async for document, new_history, temp_file in interface.generate_doc_stream(doc_type, history):
        # ドキュメントが生成されることを確認
        assert "要件定義書" in document
        # 履歴が維持されることを確認
        assert new_history == history
        # 一時ファイルが生成されることを確認
        assert isinstance(temp_file, str)
        assert temp_file.endswith(".md")
        assert os.path.exists(temp_file)


def test_build_interface(interface, mock_controller):
    """Gradioインターフェースを構築できることを確認"""
    with patch("gradio.Blocks") as mock_blocks:
        interface.build_interface()

        # Blocksが呼び出されることを確認
        mock_blocks.assert_called_once()

        # モデル選択ドロップダウンが正しく設定されることを確認
        mock_dropdown = mock_blocks.return_value.__enter__.return_value.Row.return_value.__enter__.return_value.Dropdown
        mock_dropdown.assert_called_once()
        dropdown_args = mock_dropdown.call_args[1]
        assert dropdown_args["choices"] == mock_controller.client.get_available_models.return_value
        assert dropdown_args["value"] == mock_controller.current_model
        assert dropdown_args["label"] == "モデルを選択"

        # チャットボットが正しく設定されることを確認
        mock_chatbot = mock_blocks.return_value.__enter__.return_value.Chatbot
        mock_chatbot.assert_called_once()
        chatbot_args = mock_chatbot.call_args[1]
        assert chatbot_args["label"] == "チャット履歴"
        assert chatbot_args["height"] == 500
        assert chatbot_args["type"] == "messages"

        # メッセージ入力が正しく設定されることを確認
        mock_textbox = mock_blocks.return_value.__enter__.return_value.Row.return_value.__enter__.return_value.Textbox
        assert mock_textbox.call_count >= 1
        textbox_args = mock_textbox.call_args_list[0][1]
        assert textbox_args["label"] == "メッセージを入力"
        assert "placeholder" in textbox_args
        assert textbox_args["lines"] == 3

        # ボタンが正しく設定されることを確認
        mock_button = mock_blocks.return_value.__enter__.return_value.Row.return_value.__enter__.return_value.Button
        assert mock_button.call_count >= 3  # 送信、要件定義書生成、設計書生成
