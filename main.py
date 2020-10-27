import btoandav20
import backtrader as bt
from __config__ import (IS_PRACTICE_ACCT, OANDA_API_KEY, OANDA_ACCOUNT, PAIR, BAR_TIMEFRAME, BAR_COMPRESSION)
import strategies


StoreCls = btoandav20.stores.OandaV20Store
DataCls = btoandav20.feeds.OandaV20Data
BrokerCls = btoandav20.brokers.OandaV20Broker


def run_strategy():

    cerebro = bt.Cerebro()

    brokerkwargs = dict(
        token=OANDA_API_KEY,
        account=OANDA_ACCOUNT,
        practice=IS_PRACTICE_ACCT
    )

    broker = BrokerCls(**brokerkwargs)
    cerebro.setbroker(broker)
    timeframe = bt.TimeFrame.TFrame('Minutes')  # This is what we need to load TICK data from Oanda. I have no idea why 'Ticks' breaks it, but 'Minutes' pulls tick data.

    datakwargs = dict(
        timeframe = timeframe, 
        compression = 1,          # Bar Duration - DO NOT CHANGE!  If resampling of Ticks is needed, modify that in the resample function below (values pulled form __config__.py file).
        qcheck = 0.5,             # Timeout for periodic notification/resampling/replaying check
        # historical=args.historical,
        # fromdate=fromdate,
        # bidask=args.bidask,
        # useask=args.useask,
        backfill_start = False,   # Disable backfilling at the start,
        backfill = False,         # Doesnt appear to matter if this is True or False
        bidask = True,
        reconnect = True, 
        reconntimeout = 10
    )

    DataFactory = DataCls
    data0 = DataFactory(dataname=PAIR, **datakwargs)

    if BAR_TIMEFRAME == 'Ticks':
        cerebro.replaydata(data0)
    else :
        cerebro.resampledata(data0, timeframe=bt.TimeFrame.TFrame(BAR_TIMEFRAME), compression=BAR_COMPRESSION) 

    cerebro.addstrategy(strategies.PrintPrices)

    # Set Account / Broker Data
    # cerebro.broker.setcash(cash)
    # cerebro.broker.setcommission(commission=0.0000, leverage=50)
    # cerebro.addsizer(bt.sizers.FixedSize, stake=pos_size)

    cerebro.run()



if __name__ == '__main__':
    run_strategy()
