import os, time, robin_stocks.robinhood, getpass, string, random
getpass=getpass.getpass
def login(email="Simonhchampney@gmail.com"):
    if(email=="Simonhchampney@gmail.com"):
        try:
            robin_stocks.robinhood.authentication.login()
        except:
            robin_stocks.robinhood.authentication.login(username=email, password=getpass("Password: "))
    else:
        robin_stocks.robinhood.authentication.login(username=email, password=getpass("Password: "))
def query_symbols(amt):
    templ = [] # temp set here
    for i in range(amt):
        temps="" # temp set here
        for j in range(random.randint(1,4)):
            temps+=random.choice(string.ascii_uppercase)
        tempo=robin_stocks.robinhood.stocks.get_stock_quote_by_symbol(temps) # temp set here
        if(tempo):
            templ=tempo
    return templ

login()
robin_stocks.robinhood.stocks.get_ratings("AAPL", info="summary")
print(query_symbols(200))