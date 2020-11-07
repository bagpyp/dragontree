from flask import Flask, request
import sqlite3
import os
import time
import pandas as pd
import sqlalchemy
import plotly.io as pio
import plotly.express as px


app = Flask(__name__)

# for local dev -> export DATABASE_URL=$(heroku config:get DATABASE_URL)
url = os.environ.get('DATABASE_URL')

@app.route('/record')
def collect_measurement():
    dragontree = int(request.args.get('dragontree'))
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    engine = sqlalchemy.create_engine(url)
    with engine.connect():
        l = 10000 # number of records to store/show
        l -= 1
        n = engine.execute('SELECT COUNT(*) FROM dragontree').fetchall()[0][0]
        if n > l:
            k = n - l
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
    df.set_index('time', inplace=True)
    df = df.resample('30s').mean().interpolate()
    windows = [1,5,15,30,60]
    for i in windows:
        df[f'minutes:{i}'] = df.rolling(f'{i}min').mean().voltage
    df = df.reset_index()


    # plotting
    fig = px.line(df, x='time', y=[f'minutes:{i}' for i in windows])
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=30, label="30min", step="minute", stepmode="backward"),
                dict(count=6, label="6hours", step="hour", stepmode="backward"),
                dict(count=12, label="12hours", step="hour", stepmode="backward"),
                dict(count=1, label="1day", step="day", stepmode="backward"),
                dict(label='all', step="all")
            ])
        )
    )

    pio.write_html(fig, file='index.html')
    with open('index.html') as file:
        return file.read()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

