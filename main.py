# 各種パッケージの読み込み&設定
import os
import datetime
import pandas as pd
pd.set_option('display.max_rows', None)

import requests
from termcolor import colored as cl
from twelvedata import TDClient
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20, 10)

TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY') # Twelve Data のAPIキー

# ヒストリカルデータを取得
def get_historical_data(symbol, interval, outputsize, start_date, end_date, timezone):
    td = TDClient(apikey = TWELVE_DATA_API_KEY)
    
    res = td.time_series(
              symbol = symbol,
              interval = interval,
              outputsize = outputsize,
              start_date = start_date,
              end_date = end_date,
              timezone = timezone
          ).as_json()
    
    df = pd.DataFrame(res).iloc[::-1].set_index('datetime').astype(float)
    df = df[df.index >= start_date]
    df.index = pd.to_datetime(df.index)

    return df

# 単純移動平均線を作成
def make_sma(close, span):
    return close.rolling(window = span).mean()

# 指数平滑移動平均線を作成
def make_ema(close, span):
    sma = make_sma(close, span)[:span]
    return pd.concat([sma, close[span:]]).ewm(span = span, adjust = False).mean()

# 移動平均線の傾きを作成
def make_ma_slope(ma, span):
    ma_slope = []
    
    for i in range(len(ma)):
        ma_slope.append((ma[i] - ma[i - span]) / span)
    
    return ma_slope

# 銘柄
symbol = 'AUD/JPY'

# 時間軸
interval = '1day'

# 取得件数
outputsize = 1000

# 取得開始日
start_date = '2019-01-01'

# 取得終了日
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

# タイムゾーン
timezone = 'Asia/Tokyo'

# ヒストリカルデータを取得
df = get_historical_data(symbol, interval, outputsize, start_date, end_date, timezone)

# EMA50
df['ema50'] = make_ema(df['close'], 50)
df['ema50_slope'] = make_ma_slope(df['ema50'], 1)

# チャート描画
fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw = { 'height_ratios':[3, 1] })

ax1.plot(df['close'], color = 'green', linewidth = 2, label = 'CLOSING PRICE')
ax1.plot(df['ema50'], color = 'orange', linewidth = 2, label = 'EMA50')
ax1.legend(loc = 'upper left')

ax2.bar(np.arange(len(df.index)), df['ema50_slope'].fillna(0), color = [('red' if i > 0 else 'blue') for i in df['ema50_slope']])

plt.show()
