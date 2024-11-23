from flask import Flask, request, jsonify, send_file
from pptx import Presentation
import os

app = Flask(__name__)

# 許可されたAPIキー
API_KEY = "your_secret_api_key"

# APIキー認証デコレータ
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("x_api_key") or request.headers.get("X-Api-Key")
        if not api_key:
            app.logger.warning("Missing API key in headers.")
            return jsonify({"error": "Unauthorized: API key missing"}), 401
        if api_key != API_KEY:
            app.logger.warning(f"Invalid API key: {api_key}")
            return jsonify({"error": "Unauthorized: Invalid API key"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# PPTファイルの保存パスを生成
def get_presentation_path(presentation_id):
    return f"./presentations/{presentation_id}.pptx"

# /create-slide エンドポイント
@app.route('/create-slide', methods=['POST'])
@require_api_key
def create_slide():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    presentation_id = data.get('presentationId')
    slide_layout = data.get('slideLayout', 'Title and Content')

    # 必要なフィールドが不足している場合
    if not title or not content or not presentation_id:
        return jsonify({"error": "Missing required fields"}), 400

    # PPTファイルのパスを取得
    file_path = get_presentation_path(presentation_id)

    # PPTファイルが存在しない場合は新規作成
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # ディレクトリがない場合は作成
        presentation = Presentation()
        presentation.save(file_path)

    # 既存のPPTファイルを開いてスライドを追加
    presentation = Presentation(file_path)
    slide = presentation.slides.add_slide(presentation.slide_layouts[0])
    slide.shapes.title.text = title
    slide.placeholders[1].text = content
    presentation.save(file_path)

    return jsonify({
        "success": True,
        "message": f"Slide '{title}' added to presentation '{presentation_id}' successfully.",
        "presentationId": presentation_id
    })

# /download-presentation エンドポイント
@app.route('/download-presentation', methods=['GET'])
@require_api_key
def download_presentation():
    presentation_id = request.args.get('presentationId')
    if not presentation_id:
        app.logger.error("No presentationId provided")
        return jsonify({"error": "presentationId is required"}), 400

    file_path = get_presentation_path(presentation_id)
    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        return jsonify({"error": "Presentation not found"}), 404

    return send_file(file_path, as_attachment=True)

@app.before_request
def log_api_key_from_env():
    app.logger.info(f"Configured API_KEY: {os.getenv('API_KEY')}")

@app.route('/', methods=['GET', 'HEAD'])
def root_endpoint():
    return jsonify({"message": "Welcome to the PowerPoint API!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render のデフォルトポート
    app.run(debug=True, host='0.0.0.0', port=port)
