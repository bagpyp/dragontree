from flask import Flask, request, jsonify
import sqlite3
import os
import time
import pandas as pd
import sqlalchemy

app = Flask(__name__)

url = 'postgres://jfeifvvkipgowd:f96a639e478d66558b4783c394c105239d0a1d2a700142f876d439a6239f21ab@ec2-34-234-185-150.compute-1.amazonaws.com:5432/d86psflil6tjf5'

@app.route('/record')
def collect_measurement():
    dragontree = int(request.args.get('dragontree'))
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    engine = sqlalchemy.create_engine(url)
    engine.connect()
    engine.execute(f"INSERT INTO dragontree VALUES ('{now}',{dragontree})")
    return f"Inserted moisture value {dragontree} in table 'dragontree' at time {now}"


    

@app.route('/')
def display_data():
    engine = sqlalchemy.create_engine(url)
    engine.connect()
    data = engine.execute('SELECT * FROM dragontree').fetchall()
    df = pd.DataFrame(data,columns=['time','voltage'])
    df.time = pd.to_datetime(df.time)
    df = df.set_index('time')
    return df.to_html()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

