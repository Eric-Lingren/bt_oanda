import backtrader as bt

class PrintPrices(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0) 
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):
        self.databid = self.datas[0].low
        self.dataask = self.datas[0].high
    def next(self):
        self.log('Bid, %.5f' % self.databid[0])
        self.log('Ask, %.5f' % self.dataask[0])
