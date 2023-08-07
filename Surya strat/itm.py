# import requests

# url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'

# response = requests.get(url)

# # print(response.json())
# i = 0
# for company_data in response.json():
#     print(i)
#     i+=1
#     if(company_data['symbol'] == 'NIFTY'):
#         print('found')
#         print(company_data)
#         break


import pandas as pd
import pandas_ta as ta

# Load or generate your financial data as a Pandas DataFrame
# For demonstration, let's create a sample DataFrame
data = {'Date': ['2023-01-01', '2023-01-02', '2023-01-03', ...],
        'High': [100, 105, 110, ...],
        'Low': [95, 100, 105, ...],
        'Close': [98, 103, 108, ...]}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Calculate SuperTrend indicator
df['super_trend'] = ta.super_trend(df['High'], df['Low'], df['Close'])

print(df)

