"""アプリケーションのメインエントリーポイント"""

import os
from dotenv import load_dotenv
from .openai_client import OpenAIClient
from .chat_controller import ChatController
from .gradio_interface import GradioInterface


def main():
    """アプリケーションのメインエントリーポイント"""
    # 環境変数の読み込み
    load_dotenv()

    # OpenAI APIクライアントの初期化
    client = OpenAIClient()

    # チャットコントローラーの初期化
    controller = ChatController(client)

    # Gradioインターフェースの初期化と起動
    interface = GradioInterface(controller)
    app = interface.build_interface()
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)


if __name__ == "__main__":
    main()
