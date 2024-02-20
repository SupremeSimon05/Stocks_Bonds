import robin_stocks.robinhood as rh
from datetime import datetime as dt
from time import sleep
import yfinance as yf
import select, sys, a, importlib, gc, subprocess, emailing
from emailing import log_data

gc.collect()

def update_git(message):
    #Kinda not working for some workspaces, best to just not for now
    """
    # Run git commands to commit and push changes
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", message])
    subprocess.run(["git", "push"])
    """
    pass

def reload_all_modules():
    # List all modules currently loaded
    loaded_modules = list(sys.modules.keys())

    # Reload all modules
    for module_name in loaded_modules:
        if not module_name.startswith('__'):
            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)
            except Exception as e:
                print(f"Error reloading module {module_name}: {e}")


def print_progress_bar(item, lst):
    a.move_cursor(0, a.new.get_terminal_size()[1])
    total_items, current_position = len(lst), lst.index(item) + 1
    progress = int((current_position / total_items) * 100)
    progress_bar = f"{current_position}/{total_items} [{'=' * (progress // 2) + '>' + ' ' * ((100 - progress) // 2)}]          "
    print(progress_bar, end="\r")
    
def is_adr(symbol):
    instrument_data_list = rh.get_instruments_by_symbols([symbol])
    if instrument_data_list and 'adr' in instrument_data_list[0]:
        return instrument_data_list[0]['adr']
    return False

def is_stock_at_highest(symbol, time_interval):
    try:
        stock = yf.Ticker(symbol)
        historical_data = stock.history(period=time_interval, interval="1d")
        if historical_data.empty:
            return True
        current_price = historical_data.iloc[-1]['Close']
        highest_price = historical_data['High'].max()
        return current_price >= highest_price
    except Exception as e:
        print(f"An error occurred while fetching stock data for {symbol}: {e}")
        return True

def get_ipo_stock_price(ticker):
    stock_info = yf.Ticker(ticker)
    historical_data = stock_info.history(period="max")
    try:
        ipo_date = historical_data.index[0].date()
        ipo_price = historical_data.iloc[0]['Open']
    except:
        return dt.now().date(), 0
    return ipo_date, ipo_price

def get_symbol_from_instrument_url(instrument_url):
    instrument_data = rh.helper.request_get(instrument_url, 'regular', jsonify_data=True)
    return instrument_data['symbol'] if instrument_data else None



print("\033[?25h", end="")
print("\033cLogging in...\r", end="")
rh.authentication.login()
print(12*" ", "\rLogged in")
test=int(input("Just testing? (0,1) "))
times_for_email=0
while(True):
    try:
        print("Retrieving watchlist...\r", end="")
        watchlist=rh.account.get_watchlist_by_name("not")
        print(22*" ", "\rWatchlist Retrieved")
        print("Getting buying power...\r", end="")
        cash=float(rh.profiles.load_account_profile()['portfolio_cash'])-\
            sum(float(order['price']) * float(order['quantity']) 
            for order in rh.orders.get_all_open_stock_orders() 
            if order['side'] == 'buy')
        print(22*" ", "\rRetrieved buying power: $", cash)
        if(cash>1):
            to_buy=None
            to_buys = [item['symbol'] for item in watchlist['results']]
            if(test):
                to_buys=["AAPL"]
            temp = []
            symbol_price={}
            print("Reducing possible buys [1/4]...\r", end="")
            now=dt.now().date()
            for to_buy in to_buys:
                print_progress_bar(to_buy, to_buys)
                last_price=float(rh.stocks.get_latest_price(to_buy)[0])
                symbol_price[to_buy]=last_price
                if(last_price<=50 and last_price>=1):
                    ipo_date, first_price = get_ipo_stock_price(to_buy)
                    if(first_price<last_price):
                        if((now-ipo_date).days>100):
                            temp.append(to_buy)
            to_buys = temp[:]
            a.move_cursor(0, 4)
            print("Reducing possible buys [1.5/4]...\r", end="")
            temp=[]
            for to_buy in to_buys:
                print_progress_bar(to_buy, to_buys)
                if(not is_stock_at_highest(to_buy, "day")):
                    if(not is_stock_at_highest(to_buy, "week")):
                        temp.append(to_buy)
            to_buys = temp[:]
            a.move_cursor(0, 4)
            print("Reducing possible buys [1.75/4]...\r", end="")
            temp=[]
            for to_buy in to_buys:
                print_progress_bar(to_buy, to_buys)
                if(not is_adr(to_buy)):
                    temp.append(to_buy)
            to_buys = temp[:]
            a.move_cursor(0, 4)
            print("Reducing possible buys [2/4]...   \r", end="")
            owned=[]
            temp = []
            for symb, dumb in rh.account.build_holdings().items():
                owned.append(symb)
            for to_buy in to_buys:
                print_progress_bar(to_buy, to_buys)
                if(not to_buy in owned):
                    temp.append(to_buy)
            to_buys = temp[:]
            a.move_cursor(0, 4)
            print("Reducing possible buys [3/4]...\r", end="")
            temp=[]
            for to_buy in to_buys:
                print_progress_bar(to_buy, to_buys)
                summary = rh.stocks.get_ratings(to_buy)["summary"]
                if(summary==None):
                    a.move_cursor(0, a.new.get_terminal_size()[1]-2)
                    print("Missing ratings", to_buy)
                    continue
                total = summary["num_buy_ratings"]+summary["num_hold_ratings"]+summary["num_sell_ratings"]
                if(summary["num_buy_ratings"]/total>=0.5 and summary["num_sell_ratings"]<=0.3):
                    temp.append(to_buy)
            to_buys = temp[:]
            a.move_cursor(0, 4)
            print("Reducing possible buys [4/4]...\r", end="")
            temp=[]
            orders=None
            if(to_buy):
                orders=rh.orders.get_all_stock_orders()
            for to_buy in to_buys:
                print_progress_bar(to_buy, to_buys)
                has_traded=False
                for order in orders:
                    if(to_buy==get_symbol_from_instrument_url(order['instrument'])):
                        has_traded=True
                        if(order["state"]=="filled" and order["side"]=="buy"):
                            if((dt.now()-dt.strptime(order['last_transaction_at'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()/3600>24):
                                temp.append(to_buy)
                        break
                if(not has_traded):
                    temp.append(to_buy)
            to_buys = temp[:]
            a.move_cursor(0, 5)
            print(30*" ", "\rBest buys complete: ", to_buys)
            print("Getting amount to buy...\r", end="")
            symbol_amt_to_buy={}
            for to_buy in to_buys:
                symbol_amt_to_buy[to_buy]=0
            while(cash>0):
                if(not to_buys):
                    break
                for to_buy in to_buys:
                    if(symbol_price[to_buy]<cash):
                        symbol_amt_to_buy[to_buy]+=1
                        cash-=symbol_price[to_buy]
                    else:
                        cash=0
            temp={}
            for to_buy in symbol_amt_to_buy:
                if(symbol_amt_to_buy[to_buy]>0):
                    temp[to_buy]=symbol_amt_to_buy[to_buy]
            symbol_amt_to_buy=temp.copy()
            remote_command=emailing.readLatest()
            if("STOP" in remote_command.upper()):
                #update_git("Remote paused program")
                times_for_email=emailing.send_update("Remote paused the program at "+str(dt.now()), 31)
                print("\033cRemote paused program")
                while(True):
                    remote_command=emailing.readLatest()
                    if(not "STOP" in remote_command.upper()):
                        times_for_email=emailing.send_update("Remote continued the program at "+str(dt.now()),31)
                        break
                    else:
                        sleep(60)
            print(23*" ", "\rPlacing order(s) for: ", symbol_amt_to_buy, "...\r", end = "")
            for symbol in symbol_amt_to_buy:
                order = rh.orders.order(symbol, symbol_amt_to_buy[symbol], "buy", limitPrice=symbol_price[symbol]-0.01, timeInForce="gtc")
                pass
            print((len(str(symbol_amt_to_buy))+26)*" ", "\rOrder(s) placed: ", symbol_amt_to_buy)
        print("Getting current positions...\r", end="")
        owned_to_how_much={}
        for symb, dumb in rh.account.build_holdings().items():
            quantity=int(float(dumb["quantity"]))
            if(quantity>=1):
                owned_to_how_much[symb]=quantity
        print(27*" ", "\rCurrent positions received")
        print("Reducing possible sells [1/2]...\r", end="")
        to_sells=[]
        for to_sell in owned_to_how_much.keys():
            print_progress_bar(to_sell, list(owned_to_how_much.keys()))
            summary = rh.stocks.get_ratings(to_sell)["summary"]
            total = summary["num_buy_ratings"]+summary["num_hold_ratings"]+summary["num_sell_ratings"]
            if(summary["num_buy_ratings"]/total<=0.9):
                to_sells.append(to_sell)
        a.move_cursor(0,8)
        print("Reducing possible sells [2/2]...\r", end="")
        if(test and len(to_sells)>0):
            to_sells=to_sells[0]
        temp=[]
        stocks_and_price={}
        for to_sell in to_sells:
            print_progress_bar(to_sell, to_sells)
            orders=rh.orders.get_all_stock_orders()
            for order in orders:
                if(to_sell==get_symbol_from_instrument_url(order['instrument'])):
                    if(order["state"]=="filled" and order["side"]=="buy"):
                        if((dt.now()-dt.strptime(order['last_transaction_at'], "%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds()/3600>24):
                            temp.append(to_sell)
                            stocks_and_price[to_sell]=float(order['average_price'])
                    break
        to_sells = temp[:]
        a.move_cursor(0,8)
        print(31*" ", "\rBest sells complete: ", stocks_and_price)
        remote_command=emailing.readLatest()
        if("STOP" in remote_command.upper()):
                #update_git("Remote paused program")
                times_for_email=emailing.send_update("Remote paused the program at "+str(dt.now()),31)
                print("\033cRemote paused program")
                while(True):
                    remote_command=emailing.readLatest()
                    if(not "STOP" in remote_command.upper()):
                        times_for_email=emailing.send_update("Remote continued the program at "+str(dt.now()),31)
                        break
                    else:
                        sleep(60)
        print("Selling all full stocks of best sells...\r")
        for to_sell in to_sells:
            order = rh.orders.order(to_sell, int(owned_to_how_much[to_sell]), "sell", limitPrice=stocks_and_price[to_sell]+0.02, timeInForce="gtc")
        print(39*" ", "\rAll sells complete")
        #print("Completed this set of trades, repeating in 3 hours [Press enter to skip wait]")
        #sleep(5)
        # '''
        log_data("Buy orders: "+str(symbol_amt_to_buy)+",\n"+"Sell orders: "+str(stocks_and_price)+",\n"+"Cash: $"+str(cash)+",\n"+"Owned stocks: "+str(owned)+",\n"+"Time of log: "+str(dt.now())+";\n\n")
        #update_git("Program still running, set completed at "+str(dt.now()))
        times_for_email=emailing.send_update("Buy orders: "+str(symbol_amt_to_buy)+",\n"+"Sell orders: "+str(stocks_and_price)+",\n"+"Program still running at "+str(dt.now()),times_for_email,test)
        print("\n")
        sleep(1)
        print("New set starting")
        sleep(3)
        print("\033c", end="")
        reload_all_modules()
        gc.collect()
        print("Ignore that ^")
        sleep(1.5)
        print("\033c", end="")
    except KeyboardInterrupt:
        #update_git("Program ended due to user at "+str(dt.now()))
        times_for_email=emailing.send_update("Program ended by user at "+str(dt.now()),31)
        break
    except Exception as e:
        #update_git("Error occured at "+str(dt.now())+" \nError code: "+str(e))
        times_for_email=emailing.send_update("Error happened in program, trying to continue",31)



        #"""