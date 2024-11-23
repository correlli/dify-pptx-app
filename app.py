from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/routes', methods=['GET'])
def routes():
    return jsonify({
        "routes": [
            "/create-slide (OPTIONS,POST)",
            "/download-presentation (OPTIONS,GET)",
            "/routes (GET,HEAD,OPTIONS)"
        ]
    })

@app.route('/download-presentation', methods=['GET'])
def download_presentation():
    return jsonify({"message": "Download endpoint is working!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
