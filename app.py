from flask import Flask, request, jsonify, send_file
import os

app = Flask(__name__)

# 許可されたAPIキー
API_KEY = "your_secret_api_key"

# 認証デコレータ
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("x_api_key")
        if not api_key:
            app.logger.warning("Missing API key in headers.")
            return jsonify({"error": "Unauthorized: API key missing"}), 401
        elif api_key != API_KEY:
            app.logger.warning(f"Invalid API key provided: {api_key}")
            return jsonify({"error": "Unauthorized: Invalid API key"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# スライド作成エンドポイント
@app.route('/create-slide', methods=['POST'])
@require_api_key
def create_slide():
    app.logger.info("Create Slide endpoint was called.")
    
    # リクエストデータの検証
    data = request.get_json()
    if not data:
        app.logger.error("Request body is missing or not in JSON format.")
        return jsonify({"error": "Request body is required"}), 400

    # 必須フィールドの確認
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

# プレゼンテーションファイルパスを取得
def get_presentation_path(presentation_id):
    return f"./presentations/{presentation_id}.pptx"

# プレゼンテーションダウンロードエンドポイント
@app.route('/download-presentation', methods=['GET'])
@require_api_key
def download_presentation():
    app.logger.info("Download Presentation endpoint was called.")
    
    # プレゼンテーションIDの確認
    presentation_id = request.args.get('presentationId')
    if not presentation_id:
        app.logger.error("No presentationId provided.")
        return jsonify({"error": "presentationId is required"}), 400

    # ファイルの存在確認
    file_path = get_presentation_path(presentation_id)
    app.logger.info(f"Looking for file at: {file_path}")
    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        return jsonify({"error": "Presentation not found"}), 404

    return send_file(file_path, as_attachment=True)

# リクエストの詳細をログに記録
@app.before_request
def log_request_info():
    app.logger.info(f"Request Headers: {dict(request.headers)}")
    app.logger.info(f"Request Path: {request.path}")
    if request.method in ['POST', 'PUT']:
        app.logger.info(f"Request Body: {request.get_json()}")

# メイン関数
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
