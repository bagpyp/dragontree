from flask import Flask, request, jsonify
import os
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/add')
def add():
    a = request.args.get('a')
    b = request.args.get('b')
    return jsonify(float(a) + float(b))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)