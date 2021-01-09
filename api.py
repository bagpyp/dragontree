from flask import Flask, request
import sqlite3
import os
import time
import pandas as pd
import sqlalchemy
import plotly.io as pio
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter, DayLocator

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
    df.voltage = -df.voltage
    df = df.iloc[::-1]
    df = df.reindex(df.index.union(pd.date_range(df.index[0],df.index[-1],freq='30T',normalize=True)))
    df = df.interpolate(method='time')
    df = df.resample('30T').asfreq().dropna()
    windows = [6,12,18,24]
    for i in windows:
        df[f'Hourly rolling mean: {i}'] = df.rolling(f'{i}H').mean().voltage
    df.index.name = 'time'
    df.rename(columns = {'voltage':'Raw Data'}, inplace=True)
    df.reset_index(inplace=True)
    fig = px.line(
        df,
        x = 'time',
        y = ['Raw Data'] + [f'Hourly rolling mean: {i}' for i in windows],
        title = "Moisture Level of my office plant, <em>Dragontree</em>",
        labels = {
            'value':'Capacative Soil Moisture (Volts)',
            'time':'Time (slide to scale)',
            'variable':'Upsample',
        } 
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=12, label="12 hour window", step="hour", stepmode="backward"),
                dict(count=7, label="7 day window", step="day", stepmode="backward"),
                dict(label='All', step="all")
            ])
        )
    )
    pio.write_html(fig, file='index.html')
    with open('index.html') as file:
        return file.read()

@app.route('/covid')
def display_covid_data():
    spop = pd.read_pickle('spop.pkl')
    pop = spop.to_dict()
    df = pd.read_json('https://covidtracking.com/api/states/daily')
    df.date = pd.to_datetime(df.date, format='%Y%m%d')
    #%%
    sns.set()
    fig, axes = plt.subplots(2,1, sharex = True)

    scale = {'positive':1, 'death':100}


    for i,metric in enumerate(list(scale.keys())):
        data = pd.merge(df[['date','state',metric]],df.groupby('state').death.sum().rename('total'),left_on = 'state', right_on = 'state').sort_values(by='total')
        data = data.pivot('date','state', metric)
        data = data[list(pop.keys())]
        data = data.apply(lambda x: scale[metric]*x/pop[x.name])
        data = data.append(data.max().rename('max')).sort_values('max',axis=1,ascending=False).drop('max')
        sns.lineplot(ax = axes[i], data=data, palette='Spectral')
        axes[i].legend(ncol=3, loc='upper left')
        axes[i].set_title(f'Covid {metric.title()}s per Capita per State, 2020')
        axes[i].set_ylabel('Percentage of total Population')
        axes[i].set_xlabel('Date')
        axes[i].xaxis.set_major_formatter(DateFormatter('%b %d'))
        axes[i].xaxis.set_major_locator(DayLocator(interval=7))
    plt.xticks(fontsize=6)
    fig.autofmt_xdate()
    plt.tight_layout()

    fig.save_fig('covid.jpeg')

    with open('covid.html') as file:
        return file.read()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

