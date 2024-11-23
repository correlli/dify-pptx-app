from flask import Flask, request, jsonify, send_file
import os

app = Flask(__name__)

# 許可されたAPIキー
API_KEY = "your_secret_api_key"

# 認証デコレータ
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("x_api_key")
        if api_key != API_KEY:
            app.logger.warning("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# スライド作成エンドポイント（サンプル）
@app.route('/create-slide', methods=['POST'])
@require_api_key
def create_slide():
    app.logger.info("Create Slide endpoint was called.")
    data = request.json
    if not data:
        app.logger.error("Request body is missing or not in JSON format.")
        return jsonify({"error": "Request body is required"}), 400
    
    title = data.get('title')
    content = data.get('content')
    presentation_id = data.get('presentationId')
    slide_layout = data.get('slideLayout', 'Title and Content')
    
    missing_fields = [field for field in ['title', 'content', 'presentationId'] if not data.get(field)]
    if missing_fields:
        app.logger.error(f"Missing required fields: {', '.join(missing_fields)}")
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    app.logger.info(f"Creating slide with title: {title}, content: {content}, layout: {slide_layout}")
    return jsonify({
        "success": True,
        "message": f"Slide '{title}' created successfully.",
        "presentationId": presentation_id
    })


def get_presentation_path(presentation_id):
    return f"./presentations/{presentation_id}.pptx"

# プレゼンテーションダウンロードエンドポイント
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)