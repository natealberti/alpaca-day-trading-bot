import alpaca_trade_api as tradeapi
import time
import random

#connection to API
api = tradeapi.REST('KEY', 'SECRET_KEY', base_url='https://paper-api.alpaca.markets')

class bot:

    def __init__(self, stock):

        # stock to trade
        self.STOCK = stock

        # is the bot buying or selling?
        self.is_buy = True

        # how many buy/sell iterations has the bot completed?
        self.cycles = 0

        # how much money is used in each buy order?
        self.target = 2000 # ADJUST THIS

        # buy variables (in percentages)
        self.UP_TREND_THRESHOLD = 0.3 # ADJUST THIS
        self.DIP_THRESHOLD = -0.1 # ADJUST THIS
        self.BUY_QTY = self.share_amt(self.STOCK, self.target)

        # sell variables (in percentages)
        self.PROFIT_THRESHOLD = 0.1 # ADJUST THIS
        self.STOP_LOSS_THRESHOLD = -0.3 # ADJUST THIS

        # initializing stock price
        priceObj = api.get_last_trade(self.STOCK)
        self.open_price = getattr(priceObj, 'price')

        # order IDs for stop_loss/take_profit secondary sell orders
        self.limit_ID = ''
        self.stop_ID = ''

    # main trading function, runs through purchasing a share and then setting up sell conditions
    def trade(self, cycles):

        # looping bot the desired amount of times
        while(self.check_cycles(cycles)):
            # buying phase
            if(self.is_buy):
                current_price = self.get_price(self.STOCK)
                deviation = 100*(current_price - self.open_price) / current_price
                print('Current price: $' + str(self.get_price(self.STOCK)) + '\n')
                print('Attempting to buy ' + self.STOCK + '... (dev. ' + str(deviation) + '%)')
                self.buy_attempt(deviation)

            # selling phase
            else:
                # checking if sell conditions are met
                if(len(api.list_orders()) == 0):
                    print('A sell order was issued at  $' + str(self.get_price(self.STOCK)) + '.')
                    self.is_buy = True
                    self.cycles += 1
                    return
                try:
                    root_order = api.list_orders(nested=True, status='all')[0]
                except IndexError:
                    self.is_buy = True
                    print(api.list_orders(nested=True))
                    print('try-catch block activated.')
                    return

                # extracting some data from the API about the sell orders
                limit_id = self.get_limit_id(root_order)
                limit_price = getattr(api.get_order(limit_id), 'limit_price')
                stop_id = self.get_stop_id(root_order)
                stop_price = getattr(api.get_order(stop_id), 'stop_price')

                # updating the console that no sell conditions were met
                print(self.STOCK + ' current price: $' + str(self.get_price(self.STOCK)))
                print('No updates. Take-profit at $' + limit_price + ' and stop-loss at $' + stop_price + '\n')
            time.sleep(5)

    # checking if the buy order conditions were met
    def buy_attempt(self, deviation):
        if(deviation <= self.DIP_THRESHOLD or deviation >= self.UP_TREND_THRESHOLD):
            print('Placing BUY order...')
            self.open_price = self.place_buy_order()
        else:
            print('Buy attempt REJECTED. Price out of target range.\n')

    # placing the buy order, and returning the price at which it was executed
    def place_buy_order(self):
        #flipping bot back to selling phase
        self.is_buy = False

        # detailing conditions when the sells will be executed and placing the order
        price = self.get_price(self.STOCK)
        limit_price = price + price*self.PROFIT_THRESHOLD/60 # ADJUST THIS
        stop_loss = price + price*self.STOP_LOSS_THRESHOLD/60 # ADJUST THIS
        order_obj = api.submit_order(self.STOCK, self.BUY_QTY, 'buy', 'market', 'day',
                                     order_class='bracket',
                                     take_profit={'limit_price' : limit_price},
                                     stop_loss={'stop_price' : stop_loss})

        # returning the price and messaging the console
        print('BUY order placed of ' + str(self.BUY_QTY) + ' shares at $' + str(self.get_price(self.STOCK)) + '! :) :)\n')
        return price

    # returns current price of stock
    def get_price(self, ticker):
        priceObj = api.get_last_trade(ticker)
        return getattr(priceObj, 'price')

    # returns the id to the secondary LIMIT sell order
    def get_limit_id(self, root_order):
        for i in getattr(root_order, 'legs'):
            if getattr(i, 'order_type') == 'limit':
                return getattr(i, 'id')

    # returns the id to the secondary STOP sell order
    def get_stop_id(self, root_order):
        for i in getattr(root_order, 'legs'):
            if getattr(i, 'order_type') == 'stop':
                return getattr(i, 'id')

    # returns whether the number of cycles is less than the amount specified
    def check_cycles(self, cycles):
        return self.cycles < cycles

    # adjusts the amount of shares purchased based on the stock's price
    def share_amt(self, stock, target):
        price = self.get_price(stock)
        return int(target / price)

# stocks the bot will trade in
def get_stock_list():
    return ['TSLA',
            'AAPL',
            'CGC',
            'PFE',
            'DIS',
            'NIO',
            'TSM',
            'MRNA',
            'BA',
            'PLUG',
            'LMND',]

# runs the bot
def run_bot():
    #choosing a random stock from the list to trade in
    rand = random.randint(0, len(get_stock_list()))
    stock = get_stock_list()[rand]

    #running the bot with chosen stock
    b = bot(stock)
    b.trade(1)
    print('Trading cycle finished at ' + str(time.ctime()) + '\n')

if __name__ == '__main__':
    for i in range (5):
        run_bot()
    print('Today\'s trading concluded at ' + str(time.ctime()))