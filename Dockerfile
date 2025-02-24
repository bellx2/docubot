FROM python:3.11-slim

WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# アプリケーションのコピー
COPY . .

# ポートの公開
EXPOSE 7860

# 環境変数の設定
ENV HOST=0.0.0.0
ENV PORT=7860

# アプリケーションの実行
CMD ["python", "-m", "src.main"]