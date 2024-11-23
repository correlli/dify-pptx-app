from flask import Flask, request, jsonify

app = Flask(__name__)

# エンドポイントの定義
@app.route('/create-slide', methods=['POST'])
def create_slide():
    # リクエストからデータを取得
    data = request.json
    title = data.get('title')
    content = data.get('content')
    presentation_id = data.get('presentationId')
    slide_layout = data.get('slideLayout', 'Title and Content')
    
    # スライド作成の処理（例: PowerPointスライド作成を行うコード）
    # 今回はダミーのレスポンスを返す
    return jsonify({
        "success": True,
        "message": f"Slide '{title}' created successfully."
    })

# Flaskのルート一覧を表示する
@app.route('/routes', methods=['GET'])
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = f"[{arg}]"
        methods = ','.join(rule.methods)
        url = urllib.parse.unquote(f"{rule}")
        line = f"{url} ({methods})"
        output.append(line)
    return jsonify(routes=output)


# Flaskアプリのエントリポイント
if __name__ == '__main__':
    app.run(debug=True)
