from flask import Flask, request, jsonify
import urllib

app = Flask(__name__)

# /create-slide エンドポイント
@app.route('/create-slide', methods=['POST'])
def create_slide():
    """
    スライドを作成するエンドポイント。
    リクエストボディでスライドのタイトル、コンテンツ、レイアウトを受け取る。
    """
    data = request.json  # JSONデータを取得
    title = data.get('title')
    content = data.get('content')
    presentation_id = data.get('presentationId')
    slide_layout = data.get('slideLayout', 'Title and Content')

    # レスポンス例
    return jsonify({
        "success": True,
        "message": f"Slide '{title}' created successfully.",
        "presentationId": presentation_id
    })

# /routes エンドポイント
@app.route('/routes', methods=['GET'])
def list_routes():
    """
    現在のアプリに登録されている全てのエンドポイントをリストするデバッグ用エンドポイント。
    """
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        url = urllib.parse.unquote(f"{rule}")
        line = f"{url} ({methods})"
        output.append(line)
    return jsonify(routes=output)

# Flaskアプリのエントリーポイント
if __name__ == '__main__':
    app.run(debug=True)
