import pandas as pd
import yfinance as yf
import telegram

import os
from datetime import datetime, timedelta


def get_stock_data():
    todays_date = datetime.now()
    last_working_date = todays_date - timedelta(days=max(1, (todays_date.weekday() + 6) % 7 - 3))

    with open('tickers_to_watch.txt', 'r') as f:
        tickers = f.readlines()
        tickers = list(map(lambda x: x.replace('\n', ''), tickers))
        
    stock_data = yf.download(
        tickers = ','.join(tickers), 
        interval = "1d", 
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        start=last_working_date,
        end=todays_date,
        threads = False
    )


    idx_data = yf.download(
        tickers = '^GSPC, QQQ', 
        interval = "1d", 
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        start=last_working_date,
        end=todays_date,
        threads = False
    )

    def calc_open_diff(frame):
        return (100 * (frame['Open'] - frame['Close'].shift(1))/frame['Close'].shift(1))

    diffs = stock_data.stack(level=0).reindex(columns=['Open', 'Close']).groupby(level=1).apply(calc_open_diff)
    diffs.index = diffs.index.droplevel(0)
    diffs = diffs.dropna().droplevel(level=0)

    idx_diffs = idx_data.stack(level=0).reindex(columns=['Open', 'Close']).groupby(level=1).apply(calc_open_diff)
    idx_diffs.index = idx_diffs.index.droplevel(0)
    idx_diffs = idx_diffs.dropna().droplevel(level=0)


    return diffs[abs(diffs) > 2.99].append(idx_diffs).round(1).to_dict()



if __name__ == '__main__':
    
    bot = telegram.Bot(token=os.environ['STOCKSUPORDOWNBOT_TOKEN'])
    bot.send_message(chat_id='@stocksupordown',text='hi', parse_mode=telegram.ParseMode.HTML)