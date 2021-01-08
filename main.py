#%%
import requests
import pandas as pd
import plotly.graph_objects as go
from loader_funcs import load_history

#%%
#Auth key, given by registering app with TD Ameritrade API
#My apikey.txt is gitignored
with open('apikey.txt', 'r') as api_file:
    apikey = api_file.read()

#%%
#Use load_history to create a dataframe for a ticker over a given time
'''
candles:
open - stock's open for that time period
high - stock's high for that time period
low - stock's low for that time period
close - stock's close for that time period
datetime - time of data; as UTC time minus 5 hours (approximation of time at NYSE)

Each row represents one record at the given frequency
'''

candles = load_history("TSLA", 
                        apikey,
                        periodType="day",
                        period=10,
                        frequencyType="minute", 
                        frequency=15,
                        needExtendedHoursData=False)

#If status code is anything other than 200, print to console
if type(candles) == int:
    print(candles)

#%%

#use plotly candlestick chart to graph
fig = go.Figure(data=go.Candlestick(x=candles["datetime"],
                             open=candles["open"],
                             high=candles["high"],
                             low=candles["low"],
                             close=candles["close"]))

fig.show()

#%%

#use plotly scatter graph to chart as line plot
fig = go.Figure([go.Scatter(x=candles['datetime'], y=candles['high'])])
fig.show()