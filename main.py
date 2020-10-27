import btoandav20
import backtrader as bt
from __config__ import (IS_PRACTICE_ACCT, OANDA_API_KEY, OANDA_ACCOUNT)


StoreCls = btoandav20.stores.OandaV20Store
DataCls = btoandav20.feeds.OandaV20Data
BrokerCls = btoandav20.brokers.OandaV20Broker






class PrintPrices(bt.Strategy):
    print('ran')
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0) 
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):
        self.databid = self.datas[0].low
        self.dataask = self.datas[0].high
        print(self.datas[0])
    def next(self):
        self.log('Bid, %.5f' % self.databid[0])
        self.log('Ask, %.5f' % self.dataask[0])





def run_strategy():

    cerebro = bt.Cerebro()

    storekwargs = dict(
        token=OANDA_API_KEY,
        account=OANDA_ACCOUNT,
        practice=IS_PRACTICE_ACCT
    )

    broker = BrokerCls(**storekwargs)
    cerebro.setbroker(broker)

    timeframe = bt.TimeFrame.TFrame('Minutes')
    # print(dir(bt.TimeFrame))
    print(timeframe)

    datakwargs = dict(
        timeframe=timeframe, 
        compression=1,          # Bar Duration
        qcheck=0.5,             # Timeout for periodic notification/resampling/replaying check
        # historical=args.historical,
        # fromdate=fromdate,
        # bidask=args.bidask,
        # useask=args.useask,
        backfill_start=True,   # Disable backfilling at the start,
        backfill=True,
        bidask = True,
        reconnect = True, 
        reconntimeout = 10
    )

    DataFactory = DataCls
    data0 = DataFactory(dataname="EUR_USD", **datakwargs)
    # cerebro.adddata(data0)

    cerebro.replaydata(data0, timeframe=bt.TimeFrame.Seconds, compression=5)

    cerebro.addstrategy(PrintPrices)


    # Set Account / Broker Data
    # cerebro.broker.setcash(cash)
    # cerebro.broker.setcommission(commission=0.0000, leverage=50)
    # cerebro.addsizer(bt.sizers.FixedSize, stake=pos_size)


    cerebro.run()



if __name__ == '__main__':
    run_strategy()


    print('Finished Running')
