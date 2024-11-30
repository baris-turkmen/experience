from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from my first API!"})

@app.route('/api/time', methods=['GET'])
def get_time():
    from datetime import datetime
    return jsonify({"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 