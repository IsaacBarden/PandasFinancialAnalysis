import requests
import pandas as pd

def load_history(ticker, apikey, periodType=None, period=None, frequencyType="minute", frequency=1, endDate=None, startDate=None, needExtendedHoursData=True):
    """
    Load a stock's historical information for a given time frame.
    
    Args:

        ticker: The desired stock's ticker (ex. AAPL, JNJ, NVDA) 

        apikey: TD Ameritrade's authentication token

        periodType: The type of period to show. Valid values are day, month, year, or 
                    ytd (year to date). Default is day.

        period: The number of periods to show.
                    Example: For a 2 day / 1 min chart, the values would be:

                    period: 2
                    periodType: day
                    frequency: 1
                    frequencyType: min

                    Valid periods by periodType (defaults marked with an apostrophe):

                    day: 1, 2, 3, 4, 5, 10`
                    month: 1`, 2, 3, 6
                    year: 1`, 2, 3, 5, 10, 15, 20
                    ytd: 1`

        frequencyType: The type of frequency with which a new candle is formed.
                    Valid frequencyTypes by periodType (defaults marked with an apostrophe):

                    day: minute`
                    month: daily, weekly`
                    year: daily, weekly, monthly`
                    ytd: daily, weekly`

        frequency: The number of the frequencyType to be included in each candle.
                    Valid frequencies by frequencyType (defaults marked with an apostrophe):

                    minute: 1`, 5, 10, 15, 30
                    daily: 1`
                    weekly: 1`
                    monthly: 1`

        endDay: Start date as milliseconds since epoch. If startDate and endDate are provided, 
                    period should not be provided.

        startDay: Start date as milliseconds since epoch. If startDate and endDate are provided,
                    period should not be provided.

        needExtendedHoursData: true to return extended hours data, false for regular market hours only. 
                    Default is true

    Returns:

        The candles dataframe, containing:

        open - stock's open for that time period

        high - stock's high for that time period

        low - stock's low for that time period

        close - stock's close for that time period

        datetime - time of data, using UTC minus 5hrs (to approximate NYSE time zone; doesn't account for dayling savings)

        Each row represents one record at the given frequency

        If the http status code is anything other than 200,
        the status code (int) will be returned instead of a dataframe.
    """

    needExtendedHoursData = str(needExtendedHoursData).lower()


    #Make http request
    if not endDate and not startDate:
        r = requests.get(f'https://api.tdameritrade.com/v1/marketdata/{ticker}/pricehistory?apikey={apikey}&periodType={periodType}&period={period}&frequencyType={frequencyType}&frequency={frequency}&needExtendedHoursData={needExtendedHoursData}')
    elif not period and not periodType:
        r = requests.get(f'https://api.tdameritrade.com/v1/marketdata/{ticker}/pricehistory?apikey={apikey}&frequencyType={frequencyType}&frequency={frequency}&endDate={endDate}&startDate={startDate}&needExtendedHoursData={needExtendedHoursData}')
    else:
        return "Bad parameters sent"

    #Check validity of status code
    if r.status_code == 200:
        #Load response data into a dict, then into dataframe
        stock_json = r.json()
        df = pd.DataFrame.from_dict(stock_json)
        r.close()
        return extract_candles(df["candles"])
    else:
        return r.status_code

def extract_candles(candle_series):
    """        
    When the data is first loaded, all the candlestick information is stored
    into one column of the dataframe. This extracts that information and creates
    a new dataframe with the relevant information.

    Args:
        candle_series: The "candles" column from the original dataframe.

    Returns:
        The candles dataframe, as described in the load_history function.
    """

    #Construct the first row of the candles dataframe by grabbing the first
    #record of the input series, turning that into its own series, converting 
    #that into a dataframe, and transposing.
    candle_df = pd.DataFrame(data= pd.Series(data=candle_series.iloc[0])).T

    #Do the same operation for each row and append to the candles dataframe.
    for i in range(1,candle_series.size):
        to_add = pd.Series(data=candle_series.iloc[i]).to_frame().T
        candle_df=candle_df.append(to_add, ignore_index=True)

    #Turn UNIX epoch in milliseconds into a datetime
    candle_df["datetime"] = pd.to_datetime(candle_df["datetime"], unit='ms') - pd.offsets.Hour(5)

    return candle_df