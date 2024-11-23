from flask import Flask, request, jsonify, send_file
from pptx import Presentation
import os

app = Flask(__name__)

# APIキーを直接定義
API_KEY = "MySecureAPIKey123"

@app.before_request
def log_request_headers():
    app.logger.info("\n=== Request Headers Debug ===")
    headers = dict(request.headers)
    app.logger.info(f"All Headers: {headers}")
    app.logger.info(f"Keys in headers: {list(headers.keys())}")
    app.logger.info(f"x_api_key value: {request.headers.get('x_api_key')}")
    app.logger.info("=== End Headers Debug ===\n")

def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("x_api_key")
        app.logger.info("\n=== API Key Check ===")
        app.logger.info(f"Attempting to get x_api_key from headers")
        app.logger.info(f"Received headers: {dict(request.headers)}")
        app.logger.info(f"Received API key: {api_key}")
        app.logger.info(f"Expected API key: {API_KEY}")
        app.logger.info("=== End API Key Check ===\n")

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
    app.logger.info(f"Received request data: {data}")
    
    title = data.get('title')
    content = data.get('content')
    presentation_id = data.get('presentationId')
    slide_layout = data.get('slideLayout', 'Title and Content')
    
    if not all([title, content, presentation_id]):
        app.logger.error("Missing required fields.")
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        file_path = get_presentation_path(presentation_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not os.path.exists(file_path):
            presentation = Presentation()
        else:
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
    except Exception as e:
        app.logger.error(f"Error creating slide: {str(e)}")
        return jsonify({"error": f"Failed to create slide: {str(e)}"}), 500

# /download-presentation エンドポイント
@app.route('/download-presentation', methods=['GET'])
@require_api_key
def download_presentation():
    presentation_id = request.args.get('presentationId')
    app.logger.info(f"Received request for presentationId: {presentation_id}")
    
    if not presentation_id:
        app.logger.error("No presentationId provided")
        return jsonify({"error": "presentationId is required"}), 400
        
    file_path = get_presentation_path(presentation_id)
    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        return jsonify({"error": "Presentation not found"}), 404
        a
    return send_file(file_path, as_attachment=True)

@app.route('/', methods=['GET'])
def root_endpoint():
    return jsonify({"message": "Welcome to the PowerPoint API!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)