import pandas as pd
import ccxt
import random
import numpy as np
from datetime import datetime
from time import sleep
import warnings
warnings.filterwarnings('ignore')
from pprint import pprint
import pandas_ta as ta
import time
from apscheduler.schedulers.background import BackgroundScheduler



class Tsunami:
    
    in_position = False
    long = False
    short = False
    first = False
    in_trend = False
    can_long = False
    symbols = ['BTCUSD','ETHUSD','SOLUSD','DOTUSD','ADAUSD','KAVAUSD','ATOMUSD','AVAXUSD','DOGEUSD','KSMUSD'] # Select which symbols to trade
    symbol = 'KAVAUSD' # Select a starting symbol
    runs = 10

    
    def __init__(self, time, long_time, bars, leverage):
        self.exchange = ccxt.phemex({
            'apiKey':# Input your api key,
            'secret':# Input your api secret})
        self.time = time
        self.long_time_frame = long_time
        self.bars = bars
        self.leverage = leverage
        self.long_stop_loss = 0.98 # Set your stop loss for long positions (Set at 2%)
        self.short_stop_loss = 1.02 # Set your stop loss for short positions (Set at 2%)
        self.top_long_position = 0
        self.top_short_position = 0
        self.top_long_position_exit = 0
        self.top_short_position_exit = 0

        # Set the leverage preferences    
        if Tsunami.first == False:
            Tsunami.set_leverage(self)
            Tsunami.first = True
        else:
            pass
        
    # Gathering the long timeframes on the different assets        
    def long_data_timeframe(self):
        assets = ['ETHUSD','BNBUSD','AVAXUSD','DOTUSD','KSMUSD','CVXUSD','KAVAUSD','CELOUSD','1INCHUSD']
        Tsunami.symbols = []
        random.shuffle(assets)

        # Looping through each asset to gather data
        for a in assets:
            Tsunami.symbol = a
            print('the current symbol passing through the long_data_timeframe function is: ' + a)
            long_df = pd.DataFrame(self.exchange.fetch_ohlcv(Tsunami.symbol,since=None, timeframe=self.long_time_frame, limit=self.bars))
            long_df.columns=['time','open','high','low','close','volume']
            long_df['time'] = pd.to_datetime(long_df['time'], unit='ms')
            # Make sure we are getting the most up to date data, sometimes the api to gather data can be leave out the most recent bars.
            while True:
                if len(long_df.index) < 500:
                    sleep(10)
                    long_df = pd.DataFrame(self.exchange.fetch_ohlcv(Tsunami.symbol, since=None, timeframe=self.long_time_frame, limit = self.bars))
                    long_df.columns = ['time','open','high','low','close','volume']
                    long_df['time'] = pd.to_datetime(long_df['time'], unit='ms')
                # If we have the most recent data end the loop
                elif len(long_df.index) == 500:
                    break

            # The adx is an indicator to display if an asset is trending or not.
            long_df['adx'] = long_df.ta.adx(length=20,inplace=True)['ADX_20
            
            # Rather than look at if the adx is above a certain value we check to see if it's rising to find trends as they start.
            # This reduces the indicators lag which can lead to heavy losses if you enter the position to late.
            for current in range(1,len(long_df)):
                lookback = current - 20
                if long_df.loc[current,'adx'] < 20 or long_df.loc[current, 'adx'] < long_df.loc[lookback:current,'adx'].max() -5:
                    long_df.loc[current,'in_trend'] = False
                else:
                    long_df.loc[current,'in_trend'] = True

            # If the asset is in a trend append it to a list.        
            if long_df.iloc[-1]['in_trend'] == True:
                Tsunami.symbols.append(ass)
            sleep(5)

        # If no assets are trending mark the in_trend flag to false.
        if len(Tsunami.symbols) == 0:
            Tsunami.in_trend = False
        # Print which assets are trending.
        elif len(Tsunami.symbols) > 0:
            Tsunami.in_trend = True
            print('Symbols List: ')
            print(Tsunami.symbols)
        
        print('Tsunami in_trend: ' + str(Tsunami.in_trend))
                
        return long_df
    
    
    # Check which direction the asset is trending.
    def long_short(self):
        
        ls_df = pd.DataFrame(self.exchange.fetch_ohlcv(Tsunami.symbol,since=None, timeframe=self.long_time_frame, limit=self.bars))
        ls_df.columns=['time','open','high','low','close','volume']
        ls_df['time'] = pd.to_datetime(ls_df['time'], unit='ms')

        # Make sure we have the most recent data.
        while True:
            if len(ls_df.index) < 500:
                sleep(10)
                ls_df = pd.DataFrame(self.exchange.fetch_ohlcv(Tsunami.symbol, since=None, timeframe=self.long_time_frame, limit = self.bars))
                ls_df.columns = ['time','open','high','low','close','volume']
                ls_df['time'] = pd.to_datetime(ls_df['time'], unit='ms')

            elif len(ls_df.index) == 500:
                break

        # Add the Gann Hilo indicator to the short timeframe in both a large and short lengths.
        ls_df['hilo'] = ls_df.ta.hilo(high_length=150, low_length=150,append=True)['HILO_150_150']
        ls_df['hilo_long'] = ls_df.ta.hilo(high_length=90, low_length=90,append=True)['HILO_90_90']

        # Add a flag if the shorter length Hilo is above or below the longer Hilo. 
        for current in range(1,len(ls_df.index)):
            if ls_df.loc[current,'close'] > ls_df.loc[current,'hilo'] and ls_df.loc[current,'close'] > ls_df.loc[current,'hilo_long']:
                ls_df.loc[current,'can_long'] = 1
            elif ls_df.loc[current,'close'] < ls_df.loc[current,'hilo'] and ls_df.loc[current,'close'] < ls_df.loc[current,'hilo_long']:
                ls_df.loc[current,'can_long'] = -1
            else:
                ls_df.loc[current,'can_long'] = 0
                
        # Check the last bar for long and short entry flags.        
        if ls_df.iloc[-1]['can_long'] == 0:
            Tsunami.can_long = 1
        elif ls_df.iloc[-1]['can_long'] == -1:
            Tsunami.can_long = -1
        else:
            Tsunami.can_long = 0
            
        print('Can long: ' + Tsunami.symbol + ' ' + str(Tsunami.can_long))
        sleep(5)
            
        return ls_df
        
    # Get the data for the short time frame.
    def data(self):
        df = pd.DataFrame(self.exchange.fetch_ohlcv(Tsunami.symbol, since=None, timeframe=self.time, limit = self.bars))
        df.columns = ['time','open','high','low','close','volume']
        df['time'] = pd.to_datetime(df['time'], unit='ms')

        # Make sure we have the latest data.
        while True:
            if len(df.index) < 500:
                sleep(10)
                df = pd.DataFrame(self.exchange.fetch_ohlcv(Tsunami.symbol, since=None, timeframe=self.time, limit = self.bars))
                df.columns = ['time','open','high','low','close','volume']
                df['time'] = pd.to_datetime(df['time'], unit='ms')
        
            elif len(df.index) == 500:
                break
        #------------------ To change algo strategy, change between here --------------------------------

        # Add the Gann Hilo indicators and clean up the dataframe.
        df.ta.hilo(high_length = 150, low_length = 150, append=True)
        df.ta.hilo(high_length = 250, low_length = 250, append=True)
        df.drop(columns = 'HILOl_150_150',inplace=True)
        df.drop(columns = 'HILOs_150_150',inplace=True)
        df.drop(columns = 'HILOl_250_250',inplace=True)
        df.drop(columns = 'HILOs_250_250',inplace=True)

        
        df['long'] = False
        df['short'] = False

        # Check if the current close is crossing the Hilo indicator and is in line with the larger timeframe Hilo.
        for current in range(1,len(df.index)):
            lookback = current - 10
            previous = current - 1
            
            if df.loc[current,'close'] > df.loc[current,'HILO_150_150'] and df.loc[previous,'close'] < df.loc[previous, 'HILO_150_150'] and df.loc[current,'close'] > df.loc[current,'HILO_250_250']:
                df.loc[current,'long'] = True
            elif df.loc[previous,'long'] and df.loc[current,'close'] > df.loc[current,'HILO_150_150'] and df.loc[current,'close'] > df.loc[current,'HILO_250_250']:
                df.loc[current,'long'] = True
            else:
                df.loc[current,'long'] = False
                
            if df.loc[current,'close'] < df.loc[current,'HILO_150_150'] and df.loc[previous,'close'] > df.loc[previous, 'HILO_150_150'] and df.loc[current,'close'] < df.loc[current,'HILO_250_250']:
                df.loc[current,'short'] = True
            elif df.loc[previous,'short'] and df.loc[current,'close'] < df.loc[current,'HILO_150_150'] and df.loc[current,'close'] < df.loc[current,'HILO_250_250']:
                df.loc[current,'short'] = True
            else:
                df.loc[current,'short'] = False

        return df
    
        #------------------ To change algo strategy, change between here --------------------------------
    
    # Check the balance of your account
    def get_balance(self):
        params={"type":"swap","code":"USD"}
        response = self.exchange.fetch_balance(params=params)
        free = response['free']
        balance = free['USD']
    #pprint(f'this is your usd balance {balance}') # Uncomment if you want to print your account balance

        # Gather the contract size (This changes between assets)
        markets = self.exchange.fetchMarkets()
        index = 0
        for x in markets:
            if x['id'] == Tsunami.symbol:
                market = markets[index]
                contract_size = market['contractSize']
            else:
                index+=1
    #pprint(f'this is the contract size {contract_size}') # Uncomment if you want to see the dollar amount of the contract.

        # Get the bids and asks 
        ob = self.exchange.fetch_order_book(Tsunami.symbol)
        bid = ob['bids'][0][0]
        ask = ob['asks'][0][0]
        mid_price = (ask + bid) / 2
    #print(f'this is the middle price {mid_price}') # Uncomment if you want to see the middle price.
        
        # Calculate the contract
        contract_amount = mid_price * contract_size
    #print(f'1 contract should equal about this much {contract_amount}') # # Uncomment if you want to see the dollar amount of the contract.

        # How much can you purchase
        purchase = (balance // contract_amount -1) * self.leverage
    #print(f'if you are wanting to put your whole balance in which i know you do, you will be buying {purchase} many contracts based on your account size')
    
        return purchase
    
    # Get your total contracts amount. (This is used to close the position)
    def close_size(self):
        pos = self.exchange.fetch_positions()
        index = 0
        for x in pos:
            if pos[index]['info']['symbol'] == Tsunami.symbol:
                ind = pos[index]
                ind = ind['info']
                size = ind['size']
                clo_size = int(size)
            else:
                index +=1
        return clo_size
    
    
    # Get what price we entered the trade at.
    def entry_price(self):
        entry = self.exchange.fetch_positions()
        index = 0
        for x in entry:
            if entry[index]['info']['symbol'] == Tsunami.symbol:
                poi = entry[index]
                entry_price = poi['entryPrice']    
            else:
                index+=1
                  
        return entry_price
    
    # Get the current price of the asset.
    def current_price(self):
        ob = self.exchange.fetch_order_book(Tsunami.symbol)
        bid = ob['bids'][0][0]
        ask = ob['asks'][0][0]
        current_price = (ask + bid) / 2
        
        return current_price
    
    
    
    # Set the leverage.
    def set_leverage(self):
        assets = ['ETHUSD','BNBUSD','AVAXUSD','DOTUSD','KSMUSD','CVXUSD','KAVAUSD','CELOUSD','1INCHUSD']
        for ass in assets:
            self.exchange.set_leverage(self.leverage, ass)
            
            
    # Close a long position.
    def long_position_close(self):
        # Try to close using a limit order.
        self.exchange.create_limit_sell_order(Tsunami.symbol,Tsunami.close_size(self), self.exchange.fetch_order_book(Tsunami.symbol)['asks'][0][0]) 
        sleep(120)
        # If limit order is not fulfilled cancel it and close with a market order.
        if len(self.exchange.fetch_open_orders(Tsunami.symbol)) != 0:
            self.exchange.cancel_all_orders(Tsunami.symbol)
            self.exchange.create_order(Tsunami.symbol,'market','sell',Tsunami.close_size(self))
        # Update our position statuses.
        Tsunami.in_position = False
        Tsunami.long = False
        # Print when we closed the position.
        print('Long position closed'+Tsunami.symbol +str(datetime.now()))
        # Reset variables.
        self.top_long_position = 0
        self.top_long_position_exit = 0
        Tsunami.last_trade = Tsunami.symbol
        sleep(10)
        

    # Close a short position.
    def short_position_close(self):
        # Try to close using a limit order.
        self.exchange.create_limit_buy_order(Tsunami.symbol,Tsunami.close_size(self),self.exchange.fetch_order_book(Tsunami.symbol)['bids'][0][0]) 
        sleep(120)
        # If limit order is not fulfilled cancel it and close with a market order.
        if len(self.exchange.fetch_open_orders(Tsunami.symbol)) != 0:
            self.exchange.cancel_all_orders(Tsunami.symbol)
            self.exchange.create_order(Tsunami.symbol,'market','buy',Tsunami.close_size(self)) 
        # Update our position statuses.
        Tsunami.in_position = False 
        Tsunami.short = False
        # Print when we closed the position.
        print('Short position closed'+Tsunami.symbol+str(datetime.now()))
        # Reset variables.
        self.top_short_position = 0
        self.top_short_position_exit = 0
        Tsunami.last_trade = Tsunami.symbol
        sleep(10)
            
            
    # Algo to call data and place trades.
    def algo(self):
        
        print(datetime.now())
        
        
        # Check if we are currently in a position.
        if Tsunami.in_position == True:
            # Gather the latest data.
            df = Tsunami.data(self)
            current = len(df.index) - 1
            previous = current - 1
            look_back = range(current-10,current+1)
            
            
            entry = Tsunami.entry_price(self)
            price = Tsunami.current_price(self)
            
            #calculates where we currently are in terms of pnl
            long_position = (price / entry *100) -100
            short_position = (entry / price *100) - 100
            
            # Checks if we need to gather data on the long time frame.
            if Tsunami.runs > 4:
                Tsunami.runs = 1
            
            # Prints the last 3 rows in the current datafrome.   
            print(df.iloc[-3:])
        
            # Checks if we are in a long position.
            if Tsunami.long == True:

                # Checks our current PnL to see where we need to put our trailing stop loss.
                if long_position > self.top_long_position:
                    self.top_long_position = long_position                   
                    
                if self.top_long_position > 3:
                    self.top_long_position_exit = 0.7   
                elif self.top_long_position > 2:
                    self.top_long_position_exit = 0.6
                elif self.top_long_position > 1:
                    self.top_long_position_exit = 0.5
                    
                # Checks the trailing stop to see if an exit needs to be placed.    
                if self.top_long_position > 1:
                    if long_position <= self.top_long_position * self.top_long_position_exit:
                        Tsunami.long_position_close(self)
                        print('closed on the top_long_position_exit rule')
                        # Reset variables.
                        self.top_long_position = 0
                        self.top_long_position_exit = 0
                        
                # If we have a position that has gained more than 5% close out. (This ensures that we don't lose our hard earned profits)
                if self.top_long_position > 5:
                    Tsunami.long_position_close(self)
                    print('closed on the greater than 5 rule')
                    # Reset variables.
                    self.top_long_position = 0
                    self.top_long_position_exit = 0
                        
                # Checks if we are still in position after checking the trailing stop.        
                if Tsunami.in_position == True:

                    # Checks if an exit needs to be placed based on the indicators. 
                    if not df['long'][current] or price < entry * self.long_stop_loss or price < df['close'][look_back].max() * self.long_stop_loss:
                        Tsunami.long_position_close(self)
                        print('closed on the not long rule')
                        # Reset variables.
                        self.top_long_position = 0
                        self.top_long_position_exit = 0
                        
                    else:
                        # Print the current statuses on the trade.
                        print(f'top_long_position: {self.top_long_position}')
                        print(f'top_long_position_exit: {self.top_long_position_exit}')
                        print(f'top long position exit target: {self.top_long_position * self.top_long_position_exit}')
                        print(f'Our entry price was: {entry}')
                        print(f'The current price of {Tsunami.symbol} is: {price}')
                        print(f'Still in the position with a current pnl: {round(long_position,2)}%' + str(datetime.now()))

            # Checks if we are in a short position.
            elif Tsunami.short == True:    

                # Checks our current PnL to see where we need to put our trailing stop loss.
                if short_position > self.top_short_position:
                    self.top_short_position = short_position
                    
                if self.top_short_position > 3:
                    self.top_short_position_exit = 0.7
                elif self.top_short_position > 2:
                    self.top_short_position_exit = 0.6
                elif self.top_short_position > 1:
                    self.top_short_position_exit = 0.5

                # Checks the trailing stop to see if an exit needs to be placed.    
                if self.top_short_position > 1:
                    if short_position <= self.top_short_position * self.top_short_position_exit:
                        Tsunami.short_position_close(self)
                        print('closed on the top_long_position_exit rule')
                        self.top_short_position_exit = 0
                        self.top_short_position = 0

                # If we have a position that has gained more than 5% close out. (This ensures that we don't lose our hard earned profits)
                if self.top_short_position > 5:
                    Tsunami.short_position_close(self)
                    print('closed on the greater than 7 rule')
                    self.top_short_position_exit = 0
                    self.top_short_position = 0

                # Checks if we are still in position after checking the trailing stop.
                if Tsunami.in_position == True:
                    
                    # Checks if an exit needs to be placed based on the indicators.
                    if not df['short'][current] or price > entry * self.short_stop_loss or price > df['close'][look_back].min() * self.short_stop_loss:
                        Tsunami.short_position_close(self)
                        print('closed on the not short rule')
                        self.top_short_position_exit = 0
                        self.top_short_position = 0
                        
                    else:
                        # Print the current statuses on the trade
                        print(f'top_short_position: {self.top_short_position}')
                        print(f'top_short_position_exit: {self.top_short_position_exit}')
                        print(f'top short position exit target: {self.top_short_position * self.top_short_position_exit}')
                        print(f'Our entry price was: {entry}')
                        print(f'The current price of {Tsunami.symbol} is: {price}')
                        print(f'Still in the position with a current pnl: {round(short_position,2)}%' + str(datetime.now()))

                    
        # Checks if we are not in a position.        
        if Tsunami.in_position == False:
            
            # Checks if we have assets that are trending.
            if Tsunami.in_trend == True:

                random.shuffle(Tsunami.symbols)

                # Make sure we aren't trading the same symbol as last time. (This reduces overtrading)
                for current_symbol in Tsunami.symbols:
                    if current_symbol == Tsunami.last_trade:
                        print(f'our last trade was on {Tsunami.last_trade} skipping to next asset')
                        pass
                    else:
                        # Gather the necessary data on the assets.
                        Tsunami.symbol = current_symbol
                        print("current symbol in algo function: " + str(Tsunami.symbol))
                        Tsunami.long_short(self)
                        df = Tsunami.data(self)
                        current = len(df.index) - 1
                        previous = current - 1

                        # Check if an entry signal is given.
                        if df['long'][current] and not df['long'][previous]:
                            # Place a limit order to buy long.
                            self.exchange.create_limit_buy_order(Tsunami.symbol, Tsunami.get_balance(self), self.exchange.fetch_order_book(Tsunami.symbol)['bids'][0][0]) 
                            sleep(60)
                            # If limit order is not hit enter a market order.
                            if len(self.exchange.fetch_open_orders(Tsunami.symbol)) != 0:
                                self.exchange.cancel_all_orders(Tsunami.symbol)
                                self.exchange.create_order(Tsunami.symbol,'market','buy',Tsunami.get_balance(self)) 
                            # Update variables.
                            Tsunami.in_position = True
                            Tsunami.long = True
                            print('Long position entered' + Tsunami.symbol +str(datetime.now()))
                            # If we have entered a position end the loop.
                            break
                            sleep(10)

                        # Check if a short entry is given.
                        elif df['short'][current] and not df['short'][previous]:
                            # Place a limit order to sell short.
                            self.exchange.create_limit_sell_order(Tsunami.symbol,Tsunami.get_balance(self),self.exchange.fetch_order_book(Tsunami.symbol)['asks'][0]
                            sleep(60)
                            # If a limit ordere is not hit enter a market order.
                            if len(self.exchange.fetch_open_orders(Tsunami.symbol)) != 0:
                                self.exchange.cancel_all_orders(Tsunami.symbol)
                                self.exchange.create_order(Tsunami.symbol,'market','sell',Tsunami.get_balance(self))
                            # Update variables.
                            Tsunami.in_position = True
                            Tsunami.short = True
                            print('Short position entered'+Tsunami.symbol + str(datetime.now()))
                            # If we have entere a position end the loop
                            break
                            sleep(10)
                        else:
                            print('No positions were entered at this time: ' + str(datetime.now()))
                            sleep(8)
                            
        # Update indicator to check if we need to update data on the long time frame.             
        Tsunami.runs += 1



# Inputs for timeframe and historical data.
start_bot = Tsunami('15m','4h', 500, 1)

# Initialize the scheduler for automation.
sched = BackgroundScheduler()
sched.add_job(start_bot.algo,'interval', minutes=15)
sched.start()
 
# Runs an infinite loop
while True:
    sleep(1)





