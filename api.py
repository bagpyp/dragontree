from flask import Flask, request, jsonify
import sqlite3
import os
import time
import pandas as pd
import sqlalchemy

app = Flask(__name__)

# for local dev -> export DATABASE_URL=$(heroku config:get DATABASE_URL)
url = os.environ.get('DATABASE_URL')

@app.route('/record')
def collect_measurement():
    dragontree = int(request.args.get('dragontree'))
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    engine = sqlalchemy.create_engine(url)
    with engine.connect():
        n = engine.execute('SELECT COUNT(*) FROM dragontree').fetchall()[0][0]
        if n > 10:
            k = n-10
            engine.execute\
                (\
                'DELETE FROM dragontree WHERE time IN'\
                    + '('\
                        + f'SELECT time FROM dragontree ORDER BY time ASC LIMIT {k}'\
                    + ')'\
                )
        engine.execute(f"INSERT INTO dragontree VALUES ('{now}',{dragontree})")
    
    return f"Inserted moisture value {dragontree} in table 'dragontree' at time {now}"

@app.route('/')
def display_data():
    engine = sqlalchemy.create_engine(url)
    with engine.connect():
        data = engine.execute('SELECT * FROM dragontree ORDER BY time DESC').fetchall()
    df = pd.DataFrame(data,columns=['time','voltage'])
    df.time = pd.to_datetime(df.time)
    df = df.set_index('time')
    return df.to_html(show_dimensions=True)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

