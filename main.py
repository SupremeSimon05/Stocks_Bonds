import robin_stocks.robinhood as rh
from datetime import datetime as dt
from time import sleep
import select, sys

def get_symbol_from_instrument_url(instrument_url):
    instrument_data = rh.helper.request_get(instrument_url, 'regular', jsonify_data=True)
    return instrument_data['symbol'] if instrument_data else None
def log_data(data):
    try:
        with open("log.txt", "a") as f:
            f.write(data)
    except:
        with open("log.txt", "w") as f:
            f.write(data)

print("\033cLogging in...\r", end="")
rh.authentication.login()
print(12*" ", "\rLogged in")
print("Retrieving watchlist...\r", end="")
watchlist=rh.account.get_watchlist_by_name("not")
print(22*" ", "\rWatchlist Retrieved")
while(True):
    print("Getting buying power...\r", end="")
    cash=float(rh.profiles.load_account_profile()['portfolio_cash'])-\
        sum(float(order['price']) * float(order['quantity']) 
        for order in rh.orders.get_all_open_stock_orders() 
        if order['side'] == 'buy')
    print(22*" ", "\rRetrieved buying power: $", cash)
    if(cash>1):
        to_buy=None
        to_buys = [item['symbol'] for item in watchlist['results']]
        temp = []
        symbol_price={}
        print("Reducing possible buys [1/4]...\r", end="")
        for to_buy in to_buys:
            last_price=float(rh.stocks.get_latest_price(to_buy)[0])
            symbol_price[to_buy]=last_price
            if(last_price<=10 and last_price>=1):
                temp.append(to_buy)
        to_buys = temp[:]
        print("Reducing possible buys [2/4]...\r", end="")
        owned=[]
        temp = []
        for symb, dumb in rh.account.build_holdings().items():
            owned.append(symb)
        for to_buy in to_buys:
            if(not to_buy in owned):
                temp.append(to_buy)
        to_buys = temp[:]
        print("Reducing possible buys [3/4]...\r", end="")
        temp=[]
        for to_buy in to_buys:
            summary = rh.stocks.get_ratings(to_buy)["summary"]
            total = summary["num_buy_ratings"]+summary["num_hold_ratings"]+summary["num_sell_ratings"]
            if(summary["num_buy_ratings"]/total>=0.5 and summary["num_sell_ratings"]<=0.3):
                temp.append(to_buy)
        to_buys = temp[:]
        print("Reducing possible buys [4/4]...\r", end="")
        temp=[]
        orders=None
        if(to_buy):
            orders=rh.orders.get_all_stock_orders()
        for to_buy in to_buys:
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
        print(23*" ", "\rPlacing order(s) for: ", symbol_amt_to_buy, "...\r", end = "")
        for symbol in symbol_amt_to_buy:
            order = rh.orders.order(symbol, symbol_amt_to_buy[symbol], "buy", limitPrice=symbol_price[symbol]-0.01, timeInForce="gtc")
        print((len(str(symbol_amt_to_buy))+26)*" ", "\rOrder(s) placed: ", symbol_amt_to_buy)
    print("Getting current positions...\r", end="")
    owned_to_how_much={}
    for symb, dumb in rh.account.build_holdings().items():
        quantity=int(float(dumb["quantity"]))
        if(quantity>1):
            owned_to_how_much[symb]=quantity
    print(27*" ", "\rCurrent positions received")
    print("Reducing possible sells [1/2]...\r", end="")
    to_sells=[]
    for to_sell in owned_to_how_much.keys():
        summary = rh.stocks.get_ratings(to_sell)["summary"]
        total = summary["num_buy_ratings"]+summary["num_hold_ratings"]+summary["num_sell_ratings"]
        if(summary["num_buy_ratings"]/total<=0.9):
            to_sells.append(to_sell)
    print("Reducing possible sells [2/2]...\r", end="")
    temp=[]
    stocks_and_price={}
    for to_sell in to_sells:
        orders=rh.orders.get_all_stock_orders()
        for order in orders:
            if(to_sell==get_symbol_from_instrument_url(order['instrument'])):
                if(order["state"]=="filled" and order["side"]=="buy"):
                    if((dt.now()-dt.strptime(order['last_transaction_at'], "%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds()/3600>24):
                        temp.append(to_sell)
                        stocks_and_price[to_sell]=float(order['average_price'])
                break
    to_sells = temp[:]
    print(31*" ", "\rBest sells complete: ", stocks_and_price)
    print("Selling all full stocks of best sells...\r")
    for to_sell in to_sells:
        order = rh.orders.order(to_sell, int(owned_to_how_much[to_sell]), "sell", limitPrice=stocks_and_price[to_sell]+0.02, timeInForce="gtc")
    print(39*" ", "\rAll sells complete")
    print("Completed this set of trades, repeating in 3 hours [Press enter to skip wait]")
    # '''
    log_data("Buy orders: "+str(symbol_amt_to_buy)+",\n"+"Sell orders: "+str(stocks_and_price)+",\n"+"Cash: $"+str(cash)+",\n"+"Owned stocks: "+str(owned)+",\n"+"Time of log: "+str(dt.now())+";\n\n")
    time_passed=0
    while time_passed < 3600*3:
        input_available, _, _ = select.select([sys.stdin], [], [], 1)
        if input_available:
            input()  # Read the input
            print("Time skipped.", end=" ")
            break
        else:
            time_passed += 1
            time_remaining = 3600*3 - time_passed
            print(time_remaining, "seconds remaining...\r", end="")
    if(time_passed>=3600*3):
        print(22*" ", end="\r")
    print("New set starting")
    sleep(3)
    print("\033c", end="")



    #"""