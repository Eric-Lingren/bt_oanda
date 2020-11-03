import btoandav20
import backtrader as bt
import strategies
import argparse


StoreCls = btoandav20.stores.OandaV20Store
DataCls = btoandav20.feeds.OandaV20Data
BrokerCls = btoandav20.brokers.OandaV20Broker

# Timeframes available for oanda
TIMEFRAMES = [
                bt.TimeFrame.Names[bt.TimeFrame.Ticks],
                bt.TimeFrame.Names[bt.TimeFrame.Seconds],
                bt.TimeFrame.Names[bt.TimeFrame.Minutes],
                bt.TimeFrame.Names[bt.TimeFrame.Days],
                bt.TimeFrame.Names[bt.TimeFrame.Weeks],
                bt.TimeFrame.Names[bt.TimeFrame.Months]
            ]


def run_strategy():
    args = parse_args()
    cerebro = bt.Cerebro()

    brokerkwargs = dict(
        token = args.token,
        account = args.account,
        practice = not args.live
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
        backfill_start = True,    # Disable/Enable backfilling at the start
        backfill = True,          # Perform backfilling after a disconnection/reconnection cycle
        bidask = True,
        reconnect = True, 
        reconnections = -1,
        reconntimeout = 5.0
    )

    DataFactory = DataCls
    data0 = DataFactory(dataname=args.data0, **datakwargs)

    if args.timeframe == 'Ticks': # This block is not currently working anymore
        cerebro.replaydata(data0)
    else :
        cerebro.resampledata(data0, timeframe=bt.TimeFrame.TFrame(args.timeframe), compression=args.compression) 


    # cerebro.addstrategy(strategies.PrintPrices)
    cerebro.addstrategy(strategies.RSITest)

    pos_size = 10000
    cerebro.addsizer(bt.sizers.FixedSize, stake=pos_size)

    cerebro.run()


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Test Oanda v20 integration')

    parser.add_argument('--account', default=None,
                        required=True, action='store',
                        help='Account identifier to use')
    
    parser.add_argument('--compression', default=1, type=int,
                        required=False, action='store',
                        help='Compression for Resample/Replay')

    parser.add_argument('--data0', default=None,
                        required=True, action='store',
                        help='data 0 into the system')
    
    parser.add_argument('--live', default=None,
                        required=False, action='store',
                        help='Go to live server rather than practice')
    
    parser.add_argument('--timeframe', default=TIMEFRAMES[2],
                        choices=TIMEFRAMES,
                        required=False, action='store',
                        help='TimeFrame for Resample/Replay')
    
    parser.add_argument('--token', default=None,
                        required=True, action='store',
                        help='Access token to use')

    if pargs is not None:
        return parser.parse_args(pargs)

    return parser.parse_args()


if __name__ == '__main__':
    run_strategy()
