from flask import Flask, request, jsonify
import sqlite3
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

@app.route('/setdata')   # ,method=['POST'])
def set_data():
    a = request.args.get('a')
    b = request.args.get('b')
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO data VALUES ({},{})".format(a,b))
    conn.commit()
    conn.close()
    return 'Inserted a:{} b:{}'.format(a, b)

@app.route('/data')
def get_data():
    a = request.args.get('a')
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM data where a={}".format(a))
    rows = [r for r in res]
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)