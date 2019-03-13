import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd 
import numpy as np  
import datetime as dt

def update_spreadsheet(sheetName):
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('python-sheets-40279afc8947.json', scope)

    gc = gspread.authorize(credentials)
    wksht = gc.open(sheetName).sheet1

    dataList = wksht.get_all_values()
    df = pd.DataFrame(data=dataList[1:], columns=dataList[0])
    df['Pace'] = pd.to_datetime(df['Pace'],format= '%H:%M:%S' ).dt.time
    df[['time_h','time_m','time_s']]  = df['Time'].astype(str).str.split(':', expand=True).astype(int)
    df[['pace_h','pace_m','pace_s']]  = df['Pace'].astype(str).str.split(':', expand=True).astype(int)
    df["timeSeconds"] = df.time_h*3600 + df.time_m*60 + df.time_s
    df["paceSeconds"] = df.pace_h*3600 + df.pace_m*60 + df.pace_s

    df.Date = pd.to_datetime(df['Date'],format='%m/%d/%Y')

    df.Distance = df.Distance.astype(float)
    df.MPH = df.MPH.astype(float)
    df.to_csv("data/running-log.csv")

