from flask import Flask, request, jsonify, send_file
from pptx import Presentation
import os
import logging

# ロギング設定を強化
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.debug = True
app.logger.setLevel(logging.DEBUG)

# APIキーを直接定義
API_KEY = "MySecureAPIKey123"

@app.before_request
def log_request_headers():
   app.logger.info("\n=== Request Headers Debug ===")
   headers = dict(request.headers)
   app.logger.info(f"All Headers: {headers}")
   app.logger.info(f"Keys in headers: {list(headers.keys())}")
   app.logger.info(f"x_api_key value: {request.headers.get('x_api_key')}")
   app.logger.info(f"X-Api-Key value: {request.headers.get('X-Api-Key')}")
   app.logger.info(f"X_API_KEY value: {request.headers.get('X_API_KEY')}")
   app.logger.info("=== End Headers Debug ===\n")

def require_api_key(func):
   def wrapper(*args, **kwargs):
       app.logger.info("\n=== Headers Debug ===")
       # 全てのヘッダーを出力
       for header_name, header_value in request.headers.items():
           app.logger.info(f"Header [{header_name}]: {header_value}")
       
       # 異なる方法でAPIキーを取得
       api_key = request.headers.get("x_api_key")
       api_key_2 = request.headers.get("X-Api-Key")
       api_key_3 = request.headers.get("X_API_KEY")
       
       app.logger.info(f"api_key (underscore): {api_key}")
       app.logger.info(f"api_key (hyphen): {api_key_2}")
       app.logger.info(f"api_key (uppercase): {api_key_3}")
       
       # 実際のAPIキーを取得
       actual_key = api_key or api_key_2 or api_key_3
       
       if not actual_key:
           app.logger.warning("Missing API key in headers.")
           return jsonify({"error": "Unauthorized: API key missing"}), 401
           
       if actual_key != API_KEY:
           app.logger.warning(f"Invalid API key: {actual_key}")
           return jsonify({"error": "Unauthorized: Invalid API key"}), 401
           
       return func(*args, **kwargs)
   wrapper.__name__ = func.__name__
   return wrapper

# PPTファイルの保存パスを生成
def get_presentation_path(presentation_id):
   return f"./presentations/{presentation_id}.pptx"

# create-slide エンドポイント
@app.route('/create-slide', methods=['POST'])
@require_api_key
def create_slide():
   app.logger.info("\n=== Create Slide Endpoint ===")
   app.logger.info(f"Method: {request.method}")
   app.logger.info(f"Headers: {dict(request.headers)}")

   try:
       data = request.json
       app.logger.info(f"Received request data: {data}")
       
       title = data.get('title')
       content = data.get('content')
       presentation_id = data.get('presentationId')
       
       if not all([title, content, presentation_id]):
           return jsonify({"error": "Missing required fields"}), 400
       
       file_path = get_presentation_path(presentation_id)
       os.makedirs(os.path.dirname(file_path), exist_ok=True)
       
       presentation = Presentation() if not os.path.exists(file_path) else Presentation(file_path)
       slide = presentation.slides.add_slide(presentation.slide_layouts[0])
       slide.shapes.title.text = title
       slide.placeholders[1].text = content
       presentation.save(file_path)
       
       return jsonify({
           "success": True,
           "message": f"Slide '{title}' added successfully.",
           "presentationId": presentation_id
       })
   except Exception as e:
       app.logger.error(f"Error creating slide: {str(e)}")
       return jsonify({"error": f"Failed to create slide: {str(e)}"}), 500

# /test-headers エンドポイント
@app.route('/test-headers', methods=['POST'])
def test_headers():
   app.logger.info("\n=== Test Headers Endpoint ===")
   app.logger.info(f"Method: {request.method}")
   app.logger.info(f"Headers: {dict(request.headers)}")
   app.logger.info(f"Body: {request.get_data(as_text=True)}")
   return jsonify({
       "received_headers": dict(request.headers),
       "method": request.method
   }), 200

# download-presentation エンドポイント
@app.route('/download-presentation', methods=['GET'])
@require_api_key
def download_presentation():
   presentation_id = request.args.get('presentationId')
   app.logger.info(f"Received request for presentationId: {presentation_id}")
   
   if not presentation_id:
       return jsonify({"error": "presentationId is required"}), 400
       
   file_path = get_presentation_path(presentation_id)
   if not os.path.exists(file_path):
       return jsonify({"error": "Presentation not found"}), 404
       
   return send_file(file_path, as_attachment=True)

@app.route('/', methods=['GET'])
def root_endpoint():
   app.logger.info("\n=== Root Endpoint Access ===")
   app.logger.info(f"Headers: {dict(request.headers)}")
   return jsonify({"message": "Welcome to the PowerPoint API!"}), 200

if __name__ == '__main__':
   port = int(os.environ.get('PORT', 10000))
   app.run(debug=True, host='0.0.0.0', port=port)