import backtrader as bt
import notifications



class RSITest(bt.Strategy):
    print('RSI TEST Strategy Running')
    params = (
        ('profit_target', 2),
        ('loss_target', 2),
        ('rsiperiod', 21),
        ('rsi_lower_limit', 30),
        ('rsi_upper_limit', 70),
        ('momentumperiod', 20 )
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))
        # print('\n')
        # print(self.datas[0])
        # print('\n')

    def __init__(self,pair):
        # Keep a reference to the prices line in the data[0] dataseries
        self.databid = self.datas[0].low
        self.dataask = self.datas[0].high
        self.pair=pair

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add indicators
        self.rsi = bt.indicators.RSI_SMA(self.datas[0], period=self.params.rsiperiod)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():                
                self.log('BUY ORDER EXECUTED, Price: %.5f ' % order.executed.price)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                notifications.send_sms('BUY ORDER EXECUTED')
            elif order.issell():
                self.log('SELL ORDER EXECUTED, %.2f' % order.executed.price)
                self.sellprice = order.executed.price
                self.sellcomm = order.executed.comm
                notifications.send_sms('SELL ORDER EXECUTED')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None


    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('OPERATION PROFIT, GROSS %.5f, NET %.5f' % (trade.pnl, trade.pnlcomm) )


    def notify_data(self, data, status):
        self.datastatus = data._getstatusname(status)


    def next(self):
        
        self.log('ASK, %.5f' % self.dataask[0])
        # self.log('BID, %.5f' % self.databid[0])
        # self.log('RSI, %.2f' % self.rsi[0])
        # print(self.datastatus)
        

        # Prevent trading if we are not running on live data
        if self.datastatus != 'LIVE':
            return

        # Prevent trading if an order is already pending
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Check for Long signal
            if self.rsi[0] < self.params.rsi_lower_limit:
                if (self.dataask[-2] >= self.dataask[-1]) and (self.dataask[-1] >= self.dataask[0]):
                    self.order = self.buy()
                    self.log('New Buy Order Created, %.5f' % self.dataask[0])
            # Check for Short signal
            if self.rsi[0] > self.params.rsi_upper_limit:
                if (self.dataask[-2] <= self.dataask[-1]) and (self.dataask[-1] <= self.dataask[0]):
                    self.order = self.sell()
                    self.log('New Sell Order Created, %.5f' % self.dataask[0])
        else:
            order_value = self.position.price*self.position.size
            current_value = None

            # if self.position.size > 0:
            #     print('in a long position')
            # elif self.position.size < 0:
            #     print('in a short position')

            current_value = self.dataask[0]*self.position.size
            position_profit = current_value - order_value
            self.log('Position Equity: %.2f' % position_profit)
            print('\n')


            if (position_profit >= self.params.profit_target) or (position_profit <= -self.params.loss_target):
                self.log('Closing order, %.5f' % self.dataask[0])
                self.order = self.close()
                # msg = 'Order was closed on: ' % self.pair
                # notifications.send_sms('Order was closed')
