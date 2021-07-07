# Crypto-long-short

這是一個使用 Binance api 來撈歷史k線資料分析過去一段時間較為強勢的交易對
核心想法是在牛熊市之間都希望能夠透過類似alhpa的策略去進行套利，實際操作會是做多強勢幣，做空弱勢幣
輸入自己在 Binance 的 api key, secret 後，run 這個 program 之後再輸入想要分析的天數（近幾天），就會產出依照報酬、最大回撤來排序的 dictionary
