import backtrader as bt

class RSITest(bt.Strategy):
    print('TEST Strategy Running')
    params = (
        ('profit_target', 10),
        ('loss_target', 10),
        ('rsiperiod', 21),
        ('rsi_lower_limit', 30),
        ('rsi_upper_limit', 70),
        ('momentumperiod', 20 )
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))
        with open("test.txt", "a") as file:
            file.write('%s, %s' % (dt.isoformat(), txt))
            file.write('\n')

    def __init__(self):
        # Keep a reference to the prices line in the data[0] dataseries
        self.databid = self.datas[0].low
        self.dataask = self.datas[0].high

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
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():                
                self.log(
                    'BUY EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None


    def notify_trade(self, trade):
        if trade.isclosed:
            self.log( 'OPERATION PROFIT, GROSS %.5f, NET %.5f' % (trade.pnl, trade.pnlcomm) )


    def next(self):
        # Simply log the closing price of the series from the reference
        # print('\n')
        # print('here')
        self.log('ASK, %.5f' % self.dataask[0])
        self.log('BID, %.5f' % self.databid[0])
        # self.log('RSI, %.2f' % self.rsi[0])

        # If an order is pending, break function since we cant send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Check Buy
            if self.rsi[0] < self.params.rsi_lower_limit:
                if (self.dataask[-2] >= self.dataask[-1]) and (self.dataask[-1] >= self.dataask[0]):
                    self.order = self.buy()
                    self.log('New BUY CREATE, %.5f' % self.dataask[0])
            # Check Sell 
            if self.rsi[0] > self.params.rsi_upper_limit:
                if (self.dataask[-2] <= self.dataask[-1]) and (self.dataask[-1] <= self.dataask[0]):
                    self.order = self.sell()
                    self.log('New Sell CREATE, %.5f' % self.dataask[0])

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
