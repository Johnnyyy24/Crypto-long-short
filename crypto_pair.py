from datetime import datetime, timedelta
import pandas as pd
from binance.client import Client
import matplotlib.pyplot as plt


api_key = 'your api key'
api_secret = 'your api secret'
client = Client(api_key, api_secret)
today = datetime.now()
END_DATE = str(today.day)+' '+today.strftime("%B")[:3]+', '+str(today.year)

tickers = ['BTC','ETH','DOT',
'ADA','LINK','BNB','XRP','SOL',
'EOS','AAVE','CAKE','UNI','ATOM',
'GRT','MATIC','SRM','DOGE','FIL'
]

class Preprocessing():
    def __init__(self) -> None:
        pass
    def price_preprocessing(self,klines):
        #將klines 整理成只有前五個element
        for i in range(len(klines)):
          klines[i] = klines[i][:5]
        #直接將klines轉成dataframe
        df = pd.DataFrame.from_records(klines,columns=['date','open','high','low','close'],index='date')
        return df
    def adjust_price_date(self,prices,start_time):
        date_list = [start_time]
        cur = start_time
        for i in range(len(prices)-1):
          cur_time = datetime.strptime(cur, '%Y-%m-%d %H:%M:%S')
          cur_time += timedelta(hours=1)
          cur = cur_time.strftime("%Y-%m-%d %H:%M:%S")
          date_list.append(cur)
        prices.index = date_list
        return prices
    def PricesStringToInt(self,prices): 
        targets = ['open','high','low','close']
        for target in targets:
          prices[target]= pd.to_numeric(prices[target], errors='coerce')
        return prices
    def get_prices(self,tickers):
        prices = {}
        for ticker in tickers:
          klines = client.get_historical_klines(ticker+"USDT", Client.KLINE_INTERVAL_1HOUR, "12 May, 2021", END_DATE)
          price = self.price_preprocessing(klines)
          price = self.adjust_price_date(price,'2021-05-12 08:00:00')
          price = self.PricesStringToInt(price)
          prices[ticker] = price
        return prices
class NavCalculation():
    def __init__(self) -> None:
        pass

    def get_nav(self,strong_ticker,weak_ticker):
        nav = 1
        navs = [nav]
        relative_ret = prices[strong_ticker]['return'] - prices[weak_ticker]['return']
        for ret in relative_ret:
          nav *= (1+ret)
          navs.append(nav)
        navs_series = pd.Series(navs)
        navs_series.plot()
        print(strong_ticker+'/'+weak_ticker+': {}'.format(navs[-2]))

    def get_navs(self,prices,time_period): # 取得"交易對"在近time_period天的淨值
        crop_hours = time_period * 24 # 要取最後幾小時
        navs = {}
        for ticker_ini in prices:
          for ticker_cmp in prices:
            if ticker_ini == ticker_cmp: # 相同的就不比
              continue
            else:
              nav = prices[ticker_ini]['close'] / prices[ticker_cmp]['close']
              nav = nav.iloc[-1*crop_hours:]
              nav /= nav.iloc[0] # 轉變成淨值
              navs[ticker_ini+'/'+ticker_cmp] = nav
        return navs

    def get_mdd_dict(self,navs): 
        mdd_dict = dict()
        for pair in navs:
          nav = navs[pair]
          nav_max = nav.cummax() # 累積最大值
          drawdown = (nav - nav_max) / nav_max # 從上個波峰算每天的回撤比例
          mdd = drawdown.cummin() # drawdown是負值，取cummin找出最小的（絕對值最大）的回撤
          mdd_dict[pair] = mdd.iloc[-1] #最大虧損
        mdd_dict = sorted(mdd_dict.items(), key=lambda x: x[1], reverse=True) #sort DESC
        return mdd_dict 
    def get_nav_growth(self,navs):
        nav_growth = dict()
        for ticker in navs:
          nav = navs[ticker]
          nav_growth[ticker] = nav.iloc[-1] - nav.iloc[0]
        nav_growth = sorted(nav_growth.items(), key=lambda x: x[1], reverse=True)
        return nav_growth


def main():
      time_period = int(input('backtesting period: '))
      preprocess = Preprocessing()
      nav_calculator = NavCalculation()
      prices = preprocess.get_prices(tickers)
      navs = nav_calculator.get_navs(prices,time_period)
      mdd_dict = nav_calculator.get_mdd_dict(navs)
      nav_growth = nav_calculator.get_nav_growth(navs)

      print('近{}天'.format(time_period))
      print('淨值成長前十: ',nav_growth[:10])
      print('最大回撤最小前十: ',mdd_dict[:10])



if __name__ == '__main__':
    main()



  


