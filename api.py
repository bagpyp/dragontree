from flask import Flask, request, jsonify
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
    app.run()