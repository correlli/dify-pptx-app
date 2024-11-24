from flask import Flask, request, jsonify, send_file
from pptx import Presentation
import os

app = Flask(__name__)

# 許可されたAPIキー
API_KEY = "MySecureAPIKey123"

# APIキー認証デコレータ
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("x_api_key")
        if not api_key:
            app.logger.warning("Missing API key in headers.")
            return jsonify({"error": "Unauthorized: API key missing"}), 401
        if api_key != API_KEY:
            app.logger.warning(f"Invalid API key: {api_key}")
            return jsonify({"error": "Unauthorized: Invalid API key"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# **ベースディレクトリを動的に設定する関数**
def get_presentation_path(presentation_id):
    # 実行環境に依存しないパス構成
    base_dir = os.getenv(
        "PRESENTATION_BASE_DIR", 
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "presentations")
    )
    return os.path.join(base_dir, f"{presentation_id}.pptx")

# スライド作成エンドポイント
@app.route('/create-slide', methods=['POST'])
@require_api_key
def create_slide():
    app.logger.debug("Received request at /create-slide endpoint")
    data = request.json
    title = data.get('title')
    content = data.get('content')
    presentation_id = data.get('presentationId')
    slide_layout = data.get('slideLayout', 'Title and Content')

    if not title or not content or not presentation_id:
        return jsonify({"error": "Missing required fields"}), 400

    # プレゼンテーションファイルのパス
    file_path = get_presentation_path(presentation_id)
    app.logger.debug(f"Target file path for presentation: {file_path}")

    # 必要に応じてディレクトリ作成
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # ファイルが存在しない場合は新規作成
    if not os.path.exists(file_path):
        app.logger.info(f"Creating new PowerPoint file at {file_path}")
        presentation = Presentation()
        presentation.save(file_path)

    # 既存ファイルを開いてスライドを追加
    app.logger.debug(f"Opening PowerPoint file at {file_path}")
    presentation = Presentation(file_path)
    slide = presentation.slides.add_slide(presentation.slide_layouts[0])
    slide.shapes.title.text = title
    slide.placeholders[1].text = content
    presentation.save(file_path)
    app.logger.info(f"Slide '{title}' successfully added to {presentation_id}")

    return jsonify({
        "success": True,
        "message": f"Slide '{title}' added to presentation '{presentation_id}' successfully.",
        "presentationId": presentation_id
    })

# プレゼンテーションダウンロードエンドポイント
@app.route('/download-presentation', methods=['GET'])
@require_api_key
def download_presentation():
    app.logger.debug("Received request at /download-presentation endpoint")
    presentation_id = request.args.get('presentationId')
    if not presentation_id:
        return jsonify({"error": "presentationId is required"}), 400

    file_path = get_presentation_path(presentation_id)
    app.logger.debug(f"Looking for file at: {file_path}")
    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        return jsonify({"error": "Presentation not found"}), 404

    app.logger.info(f"Serving file: {file_path}")
    return send_file(file_path, as_attachment=True)

# ルートエンドポイント
@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Welcome to the PowerPoint API!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
