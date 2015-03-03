import urllib.request, urllib.parse, urllib.error
def get_historical_prices_plus_one_day(symbol, date):
    """
    Get historical prices for the given ticker symbol.
    Returns a nested list.
    date in YYYYMMDD format
    I want the price of the day after the given day as a way to simulate the lag time of buy/sell action once a newspaper publishes a list
    I don't think that i should really be 
    
    the date goes month(jan=0) day year
    http://ichart.yahoo.com/table.csv?s=alxn&d=2012&e=11&f=03&g=d&a=2012&b=10&c=22&ignore=.csv
    http://download.finance.yahoo.com/d/quotes.csv?s=alxn&d=2012&e=11&f=03&g=dtw7&a=2012&b=10&c=22&ignore=.csv aaggh it should be m d y not y m d
    
    why does the c=... line break? would having date as a Python Date object simply this? then I could use strftime to print out the desired bits.
    it appears my date format from the script I was previously using get_historical_prices... had a diff format. there were separators in it.
    
    """
    url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
          'd=%s&' % str(int(date[4:6]) - 1) + \
          'e=%s&' % str(int(date[6:]) + 1) + \
          'f=%s&' % str(int(date[0:4])) + \
          'g=d&' + \
          'a=%s&' % str(int(date[4:6]) - 1) + \
          'b=%s&' % str(int(date[6:]) + 1) + \
          'c=%s&' % str(int(date[0:4])) + \
          'ignore=.csv'

    data=[] #python3 method ,
    try:
        days = urllib.request.urlopen(url).readlines() #urllib.urlopen --> py3k needs .request. in there
        for day in days: #day[0] holds the fields names, day[1+] holds the data values
            dayStr = str(day, encoding='utf8')
            data.append( dayStr[:-2].split(','))
            #print('his',data) #Need to fix this so that we get the close data that we want.
    except urllib.error.HTTPError as err:
        if err.code == 404: #try incrementing date again                                                                                                                               
            counter+=1
            if (counter > _CounterSentinel) :
                print("uh oh")
                done=True
                data=[["error"]]

    return data[1][6] #return the Adj Close value, this takes splits into acct #this is kinda willy nilly since we don't check that we get valid results.

def get_historical_price(symbol, date):
    """
    Get historical prices for the given ticker symbol.
    Returns a nested list.
    date in YYYYMMDD format
        
    the date goes month(jan=0) day year
    http://ichart.yahoo.com/table.csv?s=alxn&d=2012&e=11&f=03&g=d&a=2012&b=10&c=22&ignore=.csv
    http://download.finance.yahoo.com/d/quotes.csv?s=alxn&d=2012&e=11&f=03&g=dtw7&a=2012&b=10&c=22&ignore=.csv aaggh it should be m d y not y m d
    
    """
    url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
          'd=%s&' % str(int(date[4:6]) - 1) + \
          'e=%s&' % str(int(date[6:]) ) + \
          'f=%s&' % str(int(date[0:4])) + \
          'g=d&' + \
          'a=%s&' % str(int(date[4:6]) - 1) + \
          'b=%s&' % str(int(date[6:]) ) + \
          'c=%s&' % str(int(date[0:4])) + \
          'ignore=.csv'

    data=[] #python3 method ,
    output=0.0
    #print(url)

    try:
        days = urllib.request.urlopen(url).readlines() #urllib.urlopen --> py3k needs .request. in there
        for day in days: #day[0] holds the fields names, day[1+] holds the data values
            dayStr = str(day, encoding='utf8')
            data.append( dayStr[:-2].split(','))
            #this is what 'data' looks like --> [['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Clos'], ['2013-09-24', '110.09', '111.08', '108.15', '110.42', '596200', '110.4']]
        output=float(data[1][6])
    except urllib.error.HTTPError as err:
        import traceback
        print(err,symbol,date)
           
    except urllib.error.URLError as err:
        import traceback
        print(err,symbol,date)

    except Exception as err:
        import traceback
        print(err,symbol,date)

    else:
        #raise
        import traceback
        
    #return data[1][6] #return the Adj Close value, this takes splits into acct #this is kinda willy nilly since we don't check that we get valid results.

    return output


def getSharePrice(ticker):
    """
    Retrieve the current share price for the provided ticker
    
    the date goes month(jan=0) day year
    http://download.finance.yahoo.com/d/quotes.csv?s=alxn&f=l1 # gets only for today
    http://ichart.yahoo.com/table.csv?s=alxn&f=p # gets all available records
    #    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1p' #l1-> last trade wo time, p->prev close
    """

    """
    removed when placed in StockHelper.py
    if (databaseflag):
    return getSharePriceFromDatabase(ticker)
    #an 'else' isn't necessary since we will return here.
    """        
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %ticker + '&f=l1' #l1-> last trade wo time, p->prev close
    data=0.0
    try:
        days = str(urllib.request.urlopen(url).read() , encoding='utf8')  
        data = days[:-2].split(',') 
        return data[0]
    except urllib.error.HTTPError as err:
        print(err,ticker)
    except urllib.error.URLError as err:
        print(err,ticker)

    #print(data[0])
    return 0.0#data[0]  #it should never reach here.

def getShareOpenPrice(ticker):
    """
    Retrieve the current share price for the provided ticker
    
    the date goes month(jan=0) day year
    http://download.finance.yahoo.com/d/quotes.csv?s=alxn&f=l1 # gets only for today
    http://ichart.yahoo.com/table.csv?s=alxn&f=p # gets all available records
    #    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1p' #l1-> last trade wo time, p->prev close
    """
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %ticker + '&f=o0' #l1-> last trade wo time, p->prev close
    data=0.0
    try:
        days = str(urllib.request.urlopen(url).read() , encoding='utf8')  
        data = days[:-2].split(',') 
        return data[0]
    except urllib.error.HTTPError as err:
        print(err,ticker)
    except urllib.error.URLError as err:
        print(err,ticker)

    #print(data[0])
    return 0.0#data[0]


def getSharePrices(tickerlist):
    """
    Retrieve share prices of a list of tickers from yahoo finance
    ticker should be '+' delimited values
    DEPRECATED / NOT USED
    valuable as example of how to get quotes from yahoo
    """
#tickerlist should be a set of ticker symbols with '+' in between
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %tickerlist + '&f=l1'
#            url = 'http://download.finance.yahoo.com/d/quotes.csv?s=AAPL&f=l1' l1=>last trade without time.
    days = str( urllib.request.urlopen(url).read() ,encoding='utf8') #lines()
    data = [day[:-2].split(',') for day in days]
    return data
