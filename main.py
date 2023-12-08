import os, time, robin_stocks.robinhood, getpass
getpass=getpass.getpass
try:
    robin_stocks.robinhood.authentication.login()
except:
    robin_stocks.robinhood.authentication.login(username="Simonhchampney@gmail.com", password=getpass("Password: "))
print(robin_stocks.robinhood.stocks.get_ratings("AAPL", info="summary"))