import os, time, robin_stocks.robinhood, getpass, string, random, datetime
getpass=getpass.getpass
def login(email="Simonhchampney@gmail.com"):
    if(email=="Simonhchampney@gmail.com"):
        try:
            robin_stocks.robinhood.authentication.login()
        except:
            robin_stocks.robinhood.authentication.login(username=email, password=getpass("Password: "))
    else:
        robin_stocks.robinhood.authentication.login(username=email, password=getpass("Password: "))

login()
watchlist=robin_stocks.robinhood.account.get_watchlist_by_name("not")
cash=robin_stocks.robinhood.account.load_account_profile()["cash"]
if(cash>1):
    to_buys = [item['symbol'] for item in watchlist['results']]
    temp = []
    symbol_price={}
    for to_buy in to_buys:
        last_price=float(robin_stocks.robinhood.stocks.get_latest_price(to_buy)[0])
        symbol_price[to_buy]=last_price
        if(last_price<=10 and last_price>=1):
            temp.append(to_buy)
    to_buys = temp[:]
    owned=[]
    temp = []
    for symb, dumb in robin_stocks.robinhood.account.build_holdings().items():
        owned.append(symb)
    for to_buy in to_buys:
        if(not to_buy in owned):
            temp.append(to_buy)
    to_buys = temp[:]
    temp=[]
    for to_buy in to_buys:
        orders=robin_stocks.robinhood.orders.get_all_stock_orders()
        has_traded=False
        for order in orders:
            if(to_buy==order['instrument'].split('/')[-2]):
                has_traded=True
                if(order["state"]=="filled"):
                    if((datetime.datetime.now()-datetime.datetime.strptime(order['last_transaction_at'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()/3600>24):
                        temp.append(to_buy)
                else:
                    temp.append(to_buy)
        if(not has_traded):
            temp.append(to_buy)
    to_buys = temp[:]
    temp=[]
    for to_buy in to_buys:
        summary = robin_stocks.robinhood.stocks.get_ratings(to_buy)["summary"]
        total = summary["num_buy_ratings"]+summary["num_hold_ratings"]+summary["num_sell_ratings"]
        if(summary["num_buy_ratings"]/total>=0.5 and summary["num_sell_ratings"]<=0.3):
            temp.append(to_buy)
    to_buys = temp[:]
    print(to_buys)
    symbol_amt_to_buy={}
    for to_buy in to_buys:
        symbol_amt_to_buy[to_buy]=0
    while(cash>=0):
        for to_buy in to_buys:
            if(symbol_price[to_buy]<cash):
                symbol_amt_to_buy[to_buy]+=1
            else:
                cash=0
    for symbol in symbol_amt_to_buy:
        #place limit orders here
            


#print(robin_stocks.robinhood.stocks.get_ratings("LLAP")["summary"])
#print(query_symbols(200))