import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime, timedelta
import os
import gsheets as gst
import pandas as pd 
import numpy as np  
import plotly.plotly as py
import plotly.graph_objs as go

from app import app

#get last modified date
modfied_time = datetime.fromtimestamp(os.path.getmtime("data/running-log.csv"))
today = datetime.today()
daysSinceMod = today - modfied_time

#check if over a day since refresh
if daysSinceMod.days > 0:
    gst.update_spreadsheet('Running Log')
    
#load data
df = pd.read_csv("data/running-log.csv")

def get_group_by_agg_type(group = "Day", agg_type = "mean"):
    groupDF = df.groupby(by=group,as_index=False).agg({'Distance':agg_type, 
                         'MPH':agg_type, 
                         'timeSeconds':agg_type,
                         'paceSeconds':agg_type, 
                         'Date': 'count'})
    # groupDF.rename(index=str, columns={"Date": "count"}, inplace=True)
    groupDF['paceMinutes'] = groupDF.paceSeconds/60
    groupDF['Pace'] = groupDF['paceSeconds'].apply(lambda x: "{}:{}".format(str(int(divmod(x,60)[0])).zfill(2),str(int(divmod(x,60)[1])).zfill(2)))
    return groupDF



dayGrp = get_group_by_agg_type('Day', "mean")
dayGrp['Day'] = pd.Categorical(dayGrp['Day'], ["Sun", "Mon", "Tue","Wed","Thu","Fri","Sat"])
dayGrp.sort_values("Day", inplace=True)

weekGrp = get_group_by_agg_type('Week', "sum")
emptyList = [[1,0,0,0,0,0,0,0],[3,0,0,0,0,0,0,0]]
emptyWk = pd.DataFrame(emptyList, columns=weekGrp.columns.values)
weekGrp = weekGrp.append(emptyWk)
weekGrp.sort_values("Week", inplace=True)


totalMiles = df.Distance.sum()
totalTimeSeconds = df.timeSeconds.sum()
total_m, total_s = divmod(totalTimeSeconds,60)
total_h, total_m = divmod(total_m, 60)
totalTime = "{}:{}:{}".format(str(total_h).zfill(2),str(total_m).zfill(2),str(total_s).zfill(2))
totalRunDays = df.shape[0]

avgDistance = "{:.2f}".format(df.Distance.mean())
avgPace = timedelta(seconds = df['paceSeconds'].mean())
avgPace = avgPace - timedelta(microseconds=avgPace.microseconds)
avgTime =  timedelta(seconds = df.timeSeconds.mean())
avgTime = avgTime - timedelta(microseconds=avgTime.microseconds)



monthGrp = get_group_by_agg_type('Month', "sum")


layout = html.Div(children=[
    html.H1(children="Scott's Running Dashboard"),

   html.Div(children = [
        html.Div(children=[
            html.H2("Total Mileage"), html.H3(str(totalMiles))
        ], className = 'total-child'),
        html.Div(children=[
            html.H2("Total Time"), html.H3(str(totalTime))
        ], className = 'total-child'),
        html.Div(children=[
            html.H2("Total Run Days"), html.H3(str(totalRunDays))
        ], className = 'total-child'),

        html.Div(children=[
            html.H2("Average Distance"), html.H3(str(avgDistance))
        ], className = 'total-child'),
        html.Div(children=[
            html.H2("Average Time"), html.H3(str(avgTime))
        ], className = 'total-child'),
        html.Div(children=[
            html.H2("Average Pace"), html.H3(str(avgPace))
        ], className = 'total-child')

   ], className = 'totals-container')
   ,

    
    dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x=dayGrp.Day,
                    y=dayGrp.Distance,
                    text = round(dayGrp.Distance,2),
                    hoverinfo = 'text',
                    name='Average Distance',
                    marker= go.Marker(
                        color='rgb(55, 83, 109)'
                    )
                ),
               
                go.Bar(
                    x=dayGrp.Day,
                    y=dayGrp.paceMinutes,
                    text = dayGrp.Pace,
                    hoverinfo = 'text',
                    name='Average Pace',
                    marker=go.Marker(
                        color='rgb(26, 118, 255)'
                    )
                
                )
                , go.Bar(
                    x=dayGrp.Day,
                    y=dayGrp.Date,
                    text = dayGrp.Date,
                    hoverinfo = 'text',
                    name='Running Days',
                    marker=go.Marker(
                        color='rgb(26, 255, 255)'
                    )
                )
            ],
            layout=go.Layout(
                title='Average by Day',
                showlegend=True,
                legend=go.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.Margin(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 300},
        id='my-graph'
    ),
        dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x = weekGrp.Week,
                    y = weekGrp.Distance,
                    mode = 'lines+markers',
                    name = 'Weekly Distance'
                )
                
            ],
            layout=go.Layout(
                title='Weekly Mileage',
                showlegend=True,
                legend=go.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.Margin(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 300},
        id='week-graph'
    ),
    dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x = monthGrp.Month,
                    y = monthGrp.Distance,
                    name = 'Monthly Mileage',
                     marker=go.Marker(
                        color='rgb(55, 83, 109)'
                    )
                    
                ),
                go.Bar(
                    x=monthGrp.Month,
                    y=monthGrp.Date,
                    name='Running Days',
                    marker=go.Marker(
                        color='rgb(26, 118, 255)'
                    )
                )
                
            ],
            layout=go.Layout(
                title='Monthly Mileage',
                showlegend=True,
                legend=go.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.Margin(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 300},
        id='month-graph'
    )
])

# if __name__ == '__main__':
#     app.run_server(debug=True)