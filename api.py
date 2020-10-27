from flask import Flask, request, jsonify
import sqlite3
import os
import time
import sqlalchemy

app = Flask(__name__)

@app.route('/record')
def collect_measurement():
    dragontree = int(request.args.get('dragontree'))
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    engine = sqlalchemy.create_engine('postgres://ynumvhqilbxvod:590b20a0b406d7b78c825d36151de44e5bd1ecbc53529c0db3c4f50685443093@ec2-3-216-92-193.compute-1.amazonaws.com:5432/d8keu230b7fs9s')
    engine.connect()
    engine.execute(f"INSERT INTO dragontree VALUES ('{now}',{dragontree})")
    return f"Inserted moisture value {dragontree} in table 'dragontree' at time {now}"

@app_route('/')
def display_data():
    engine = sqlalchemy.create_engine('postgres://ynumvhqilbxvod:590b20a0b406d7b78c825d36151de44e5bd1ecbc53529c0db3c4f50685443093@ec2-3-216-92-193.compute-1.amazonaws.com:5432/d8keu230b7fs9s')
    engine.connect()
    data = engine.execute('SELECT * FROM dragontree')
    sheet = ''.join([str(row)+'\n' for row in data])
    return sheet

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)