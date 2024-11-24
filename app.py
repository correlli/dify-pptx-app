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

# リクエストヘッダーをログに記録
@app.before_request
def log_request_headers():
    app.logger.info(f"Request headers: {dict(request.headers)}")

# PPTファイルの保存パスを生成
def get_presentation_path(presentation_id):
    # 必要であれば /tmp ディレクトリを使用
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

    if not title or not content or not presentation_id:
        return jsonify({"error": "Missing required fields"}), 400

    file_path = get_presentation_path(presentation_id)

    try:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            app.logger.info(f"Creating new presentation at: {file_path}")
            presentation = Presentation()
            presentation.save(file_path)

        presentation = Presentation(file_path)
        slide = presentation.slides.add_slide(presentation.slide_layouts[0])
        slide.shapes.title.text = title
        slide.placeholders[1].text = content
        presentation.save(file_path)

        app.logger.info(f"Slide added successfully to {file_path}")
        return jsonify({
            "success": True,
            "message": f"Slide '{title}' added to presentation '{presentation_id}' successfully.",
            "presentationId": presentation_id
        })
    except Exception as e:
        app.logger.error(f"Failed to create slide: {e}")
        return jsonify({"error": f"Failed to create slide: {e}"}), 500

# /download-presentation エンドポイント
@app.route('/download-presentation', methods=['GET'])
@require_api_key
def download_presentation():
    presentation_id = request.args.get('presentationId')
    if not presentation_id:
        return jsonify({"error": "presentationId is required"}), 400

    file_path = get_presentation_path(presentation_id)
    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        return jsonify({"error": "Presentation not found"}), 404

    try:
        app.logger.info(f"Sending file: {file_path}")
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Failed to send file: {e}")
        return jsonify({"error": f"Failed to send file: {e}"}), 500

# ルートエンドポイント
@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Welcome to the PowerPoint API!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
