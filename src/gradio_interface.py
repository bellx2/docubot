"""Gradioインターフェースを管理するモジュール"""

from typing import List, Dict, Generator
import tempfile
from pathlib import Path
import gradio as gr
from .chat_controller import ChatController


class GradioInterface:
    """Gradioインターフェースを管理するクラス"""

    def __init__(self, controller: ChatController):
        """
        GradioInterfaceを初期化します。

        Args:
            controller (ChatController): チャットコントローラーインスタンス
        """
        self.controller = controller
        self.temp_dir = Path(tempfile.mkdtemp())

    async def chat_stream(
        self,
        message: str,
        history: List[Dict[str, str]],
        model: str,
    ) -> Generator[tuple, None, None]:
        """
        チャットストリームを処理します。

        Args:
            message (str): ユーザーメッセージ
            history (List[Dict[str, str]]): チャット履歴
            model (str): 選択されたモデル

        Yields:
            tuple: (空文字列, 更新されたチャット履歴)
        """
        if model != self.controller.current_model:
            self.controller.change_model(model)

        response = ""
        async for chunk in self.controller.process_message(message):
            response += chunk
            # OpenAI形式のメッセージを作成
            new_history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}]
            yield "", new_history

    async def generate_doc_stream(self, doc_type: str, history: List[Dict[str, str]]) -> Generator[tuple, None, None]:
        """
        ドキュメントをストリーミング生成します。

        Args:
            doc_type (str): ドキュメントタイプ
            history (List[Dict[str, str]]): チャット履歴

        Yields:
            tuple: (生成されたドキュメント, チャット履歴, 一時ファイルパス)
        """
        document = ""
        temp_file = self.temp_dir / f"{doc_type}.md"

        async for chunk in self.controller.generate_document(doc_type):
            document += chunk
            # 一時ファイルに書き込み
            temp_file.write_text(document, encoding="utf-8")
            yield document, history, str(temp_file)

    def build_interface(self) -> gr.Blocks:
        """
        Gradioインターフェースを構築します。

        Returns:
            gr.Blocks: 構築されたGradioインターフェース
        """
        with gr.Blocks() as interface:
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    choices=self.controller.client.get_available_models(),
                    value=self.controller.current_model,
                    label="モデルを選択",
                )

            chatbot = gr.Chatbot(
                label="チャット履歴",
                height=500,
                type="messages",  # OpenAI形式のメッセージを使用
            )

            with gr.Row():
                message = gr.Textbox(label="メッセージを入力", placeholder="ここにメッセージを入力してください...", lines=3)
                send = gr.Button("送信")

            with gr.Row():
                requirements_btn = gr.Button("要件定義書を生成")
                design_btn = gr.Button("設計書を生成")

            with gr.Row():
                generated_doc = gr.Textbox(label="生成されたドキュメント", lines=20, interactive=True)
                doc_download = gr.File(label="ダウンロード", file_types=[".md"], interactive=False)

            # イベントハンドラの設定
            send.click(self.chat_stream, inputs=[message, chatbot, model_dropdown], outputs=[message, chatbot])

            message.submit(self.chat_stream, inputs=[message, chatbot, model_dropdown], outputs=[message, chatbot])

            # 要件定義書生成
            requirements_btn.click(
                self.generate_doc_stream,
                inputs=[
                    gr.State("requirements"),  # doc_type
                    chatbot,
                ],
                outputs=[generated_doc, chatbot, doc_download],
            )

            # 設計書生成
            design_btn.click(
                self.generate_doc_stream,
                inputs=[
                    gr.State("design"),  # doc_type
                    chatbot,
                ],
                outputs=[generated_doc, chatbot, doc_download],
            )

        return interface
