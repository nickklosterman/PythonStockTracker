#!/usr/bin/python3
#usage:
# python StockTrackerJSON.py -i AllPortfolios.json -a 8 #alerts if share price is 8% lower than when bought.
# python StockTrackerJSON.py -i AllPortfolios.json -s
# python StockTrackerJSON.py -i AllPortfolios.json -c

import datetime
import urllib.request, urllib.parse, urllib.error
import smtplib #for emailing reports
import os #for converting ~ -> users home directory
import json
#import pymongo #for mongodb
import ast #for literal_eval for converting string to dict

"""
Any note of 'tax' in this program uses tax algorithms for US taxes. For other countries adjust accordingly
As tax laws constantly change, these calculations should be taken with a huge grain of salt.
"""


"""
  ANSI COLOR CODING OF TERMINAL 

use ansi color codes to color fg and bg : http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html; curses is an alternative
"""

def DefaultColorCoding():
    """
    Use ansi color codes to set the terminal output to the default color coding
    """
    print(("\033[49m \033[39m "), end=' ') #set to default color coding, suppress newline


def ColorCode10pt2f(number):
    """
    use ansi color code to color text green if positive, red if negative
    color coding stays until the ansi terminal is set back to the default color coding. Call DefaultColorCoding()
    output with two decimal places of precision
    """
    if number>0: 
        print(("\033[32m %10.2f"% (number)), end=' ') #suppress newline
    else:
        print(("\033[31m %10.2f"% (number)), end=' ') 


def ColorCode10pt2fRelative(number,comparedto):
    """
    use ansi color code to color text green if value1 greater than value2, red if less than
    color coding stays until the ansi terminal is set back to the default color coding. Call DefaultColorCoding()
    output with two decimal places of precision
    """
    if number>comparedto: 
        print(("\033[32m %10.2f"% (number)), end=' ') #suppress newline
    else:
        print(("\033[31m %10.2f"% (number)), end=' ') 


def ColorCode8s(string):
    """
    use ansi color code to display string as red text
    color coding stays until the ansi terminal is set back to the default color coding. Call DefaultColorCoding()
    Currently not used anywhere
    """
    print(("\033[31m %8s"% (string)))



"""
  HTML COLOR CODING

"""

def htmlTableColorCode(value):
    """
    apply a css class to  color text green if positive, red if negative
    defaults to no color styling if not > or < 
    """
    if value > 0:
        output="<span class=\"positive\"> {:03,.2f}</span>".format(value)  #this formattting uses a comma as a separator for numbers, and outputs only two decimal places of the number
    elif value < 0:
        output="<span class=\"negative\"> {:03,.2f}</span>".format(value)
    else:
        output=value
    return output

def htmlTableComparisonColorCode(value1,value2):
    """
    apply a css class to  color text green if value1 > value 2,  red if vice versa
    defaults to no color styling if not > or < 
    """
    if value1 > value2:
        output="<span class=\"positive\"> {:03,.2f}</span>".format(value1)  #this formattting uses a comma as a separator for numbers, and outputs only two decimal places of the number
    elif value1 <value2:
        output="<span class=\"negative\"> {:03,.2f}</span>".format(value1)
    else:
        output=value1
    return output


def isLeapYear(year):
    """
    Determine if the year is a leap year
    return 1 if the year is a leap year
    """
    leapyear=0
    if year%4==0:
        leapyer=1
    return leapyear

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

 
def getUsernamePassword(file):
    """
    Get username and password from an external file
    the username should be on the first line, the password should be on the second line.
    """
    import linecache 
    username=linecache.getline(file,1) #username on 1st line
    password=linecache.getline(file,2) #password on 2nd line
    return username.strip(),password.strip()  #remove the CRLF


def emailReport(Host,Port,User,Password,From,To,Subject,Message):
    try:
        User,Password = getUsernamePassword(os.path.expanduser("~/.gmaillogin"))
        server=smtplib.SMTP()
        server.connect(Host,Port)
        server.starttls()
#        server.set_debuglevel(1)   
        server.login(User,Password)
        server.sendmail(From,[To],Message)
        server.quit()
        print("Successfully sent email")
    except smtplib.SMTPException:
        print("Error: unable to send email:%s" % smtplib.SMTPException)

def txtReport(Host,User,Password,From,To,Subject,Message):
    try:
        server=smtplib.SMTP(Host)
        server.login(User,Password)
        server.sendmail(From,[To],Message)
        server.quit()
    except smtp.SMTPException:
        print("Error sending text message")

def PrintHeader():
    """ 
    output header for 11 values currently defined and try to format the width of each to accommodate the data
    DEPRECATED
    """
    print(("%7s %10s %10s %10s %10s %10s %10s %10s %10s %10s %6s"  % ("ticker","$ gain", "ann %","% gain","Curr Worth", "Today chg$","Curr Price", "Prev Close" , "52 High","52 Low", "Trend") ))


def PrintHeader2():
    """ 
    output header for 17 values currently defined and try to format the width of each to accommodate the data
    """
    print(("%s %s %12s %12s %12s %12s %12s %12s %2s %12s %6s %12s %12s %12s %5s %12s %3s "  % ("ticker","$ gain", "ann %","% gain","Curr Worth", "Today chg $","Curr Price", "Prev Close" , "52 High","52 Low", "Trend", "Sale Tk Home","Sale Taxes","Disc4Taxes", "HiLoPct","Value if invested in SP500","Years Held") ))


def PrintBanner(input):
    """
    print banner text
    used to ouput the portfolio/filename that is being processed
    """ 
    print("#######################################################################")
    print('                          ',input)
    print("#######################################################################")



class Accumulator:
    """
    Class used to accumulate the gains and losses across the entire portfolio
    
    """
    def __init__(self):
        self.totalpurchaseprice=0.0
        self.totalcommission=0.0
        self.totaldollargain=0.0
        self.totallosses=0.0
        self.totalgains=0.0
        self.dailydollargain=0.0
        self.dailytotallosses=0.0
        self.dailytotalgains=0.0
        self.portfolioworth=0.0
        self.dailypercentchange=0.0
    def Add(self, purchaseprice, commission, dollargain,dailygain,currentworth):
        """
        Add data to the appropriate fields for the accumulator
        """
        self.totalpurchaseprice+=purchaseprice
        self.totalcommission+=commission
        self.totaldollargain+=dollargain
        if dollargain < 0.0:
            self.totallosses+=dollargain
        else:
            self.totalgains+=dollargain
        if dailygain < 0.0:
            self.dailytotallosses+=dailygain
        else:
            self.dailytotalgains+=dailygain
        self.portfolioworth+=currentworth
    def CalculateDailyPercentChange(self):
        """
        Calculate the daily percentage change of the portfolio up to that time
        
        """
        self.dailypercentchange=((self.dailytotalgains+self.dailytotallosses)/(self.portfolioworth-self.dailytotallosses-self.dailytotalgains)*100)


    def Print(self):
        """
        Print the Accumulator fields
        gains field is ansi colored green
        losses field is ansi colored red
        """
        print("")
        print(("%22s %10.2f" % ("Total Purchase Price:",self.totalpurchaseprice)))
        print(("%22s %10.2f" % ("Total Commission Paid:",self.totalcommission)))
        print(("%22s %10.2f" % ("Total Gain/Loss:",self.totaldollargain))) #this is just the total of self.totallosses+self.totalgains
        print(("%27s %10.2f %s" % ("Total Dollar Losses:\033[31m" ,self.totallosses, " \033[39m" )))
        print(("%27s %10.2f %s" % ("Total Dollar Gains:\033[32m" ,self.totalgains, " \033[39m" )))
        print(("%22s %10.2f" % ("Daily Losses:",self.dailytotallosses)))
        print(("%22s %10.2f" % ("Daily Gains:",self.dailytotalgains)))
        print(("%22s %10.2f" % ("Daily Change:",self.dailytotalgains+self.dailytotallosses)))
        self.CalculateDailyPercentChange()

        print(("%22s %10.2f" % ("Daily % Change:", self.dailypercentchange )))
        print(("%22s %10.2f" % ("Portfolio Worth:",self.portfolioworth)))



    def JSONify(self):
        """
        Create and return the Accumulator fields as a json object
        """
        #self.CalculateDailyPercentChange()
        jsonData = json.dumps({
            "Total Purchase Price":self.totalpurchaseprice,
            "Total Commission Paid":self.totalcommission,
            "Total Gain/Loss":self.totaldollargain,
            "Total Dollar Losses":self.totallosses, 
            "Total Dollar Gains":self.totalgains, 
            "Daily Losses":self.dailytotallosses,
            "Daily Gains":self.dailytotalgains,
            "Daily Change":self.dailytotalgains+self.dailytotallosses,
            "Daily % Change": self.dailypercentchange,
            "Portfolio Worth":self.portfolioworth
        } )
        return jsonData

    def HTMLTableOutput(self):
        """
        Output Accumulator fields in html to be added to a table
        
        used as prep to output portfolio / stock data  using createHTMLOutput()
        """
        separator="</th><td>"
        endseparator="</td><td colspan=\"12\"><td></tr><tr><th colspan=\"4\">"
        output="""<tr><th colspan=\"4\">Total Purchase Price {0} {2:,.2f} {1}             
        Total Commission Paid{0}{3:,.2f}{1}
            Total Gain/Loss{0}{4:,.2f}{1}
            Total Dollar Losses{0}{5:,.2f}{1}
            Total Dollar Gains{0}{6:,.2f}{1}
            Daily Losses{0}{7:,.2f}{1}
            Daily Gains{0}{8:,.2f}{1}
            Daily Change{0}{9:,.2f}{1}
            Daily % Change{0}{10:.2f}{1} 
            Portfolio Worth{0}{11:,.2f} {1} </td><td colspan=\"12\"><td></tr>
 """.format(separator,endseparator,
self.totalpurchaseprice,
self.totalcommission,
self.totaldollargain,
self.totallosses,
 self.totalgains,
 self.dailytotallosses,
self.dailytotalgains,
self.dailytotalgains+self.dailytotallosses,
self.dailypercentchange,
self.portfolioworth)
        return output
            
'''
class Compare:
take a Stock object and Compare it to a given ComparisonStock

allow a special keyword for a ComparisonStock that will allow a given return i.e. 10% annual return.
'''


def padDate(MMDDYYYYDate):
    """
    I believe it takes a date such as 7/13/1978 and converts to 07131978
    I think I wrote this as a helper for convertToYYYYMMDD() yet it appears that strftime takes care of the padding
    NOT USED
    http://docs.python.org/2/library/time.html
    """
    if len(MMDDYYYYDate)!=10:
        temp=MMDDYYYYDate.split('/')
        purchasedate=datetime.date(int(temp[2]),int(temp[0]),int(temp[1]))
        paddedDate=strftime("%m%d%Y")
    else:
        paddedDate=MMDDYYYYDate
    return paddedDate

def convertToYYYYMMDD(MMDDYYYYDate):# don't need to pad date as the strftime takes care of padding it.
    """
    Take MM/DD/YYYY format and return YYYYMMDD format of date
    I feel like there is most likely a python time function that does this conversion for me.
    """
    temp=MMDDYYYYDate.split('/')
    tempdate=datetime.date(int(temp[2]),int(temp[0]),int(temp[1]))
    return tempdate.strftime("%Y%m%d")
    
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
    days = urllib.request.urlopen(url).readlines() #urllib.urlopen --> py3k needs .request. in there
    data=[] #python3 method ,
    for day in days: #day[0] holds the fields names, day[1+] holds the data values
        dayStr = str(day, encoding='utf8')
        data.append( dayStr[:-2].split(','))
        #print('his',data) #Need to fix this so that we get the close data that we want.
    return data[1][6] #return the Adj Close value, this takes splits into acct #this is kinda willy nilly since we don't check that we get valid results.


def getSharePrice(ticker):
    """
    Retrieve the current share price for the provided ticker
    
    the date goes month(jan=0) day year
    http://download.finance.yahoo.com/d/quotes.csv?s=alxn&f=l1 # gets only for today
    http://ichart.yahoo.com/table.csv?s=alxn&f=p # gets all available records
    #    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1p' #l1-> last trade wo time, p->prev close
    """
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %ticker + '&f=l1' #l1-> last trade wo time, p->prev close
    days = str(urllib.request.urlopen(url).read() , encoding='utf8')  
    data = days[:-2].split(',') 
    #print(data[0])
    return data[0]


class MiniStock:
    """
    class to allow easy comparison to SP500,Nasdaq performance over same period
    I really need an all purpose method to do comparisons
    """
    def __init__(self,data):
        self.ticker=data['ticker']
        temp=data["purchaseDate"].split('/')
        self.purchaseDate=datetime.datetime(int(temp[2]),int(temp[0]),int(temp[1]))
        self.totalPurchasePrice=data['totalPurchasePrice']
        self.commissionToBuy=data['commissionToBuy']
        self.unitPriceAtPurchase=get_historical_prices_plus_one_day(self.ticker,(self.purchaseDate.strftime('%Y%m%d')))
        self.unitPriceAtPresent=getSharePrice(self.ticker)

       
    def GetGainLoss(self):
        return float(self.unitPriceAtPresent)/float(self.unitPriceAtPurchase)
    def GetProfit(self):
        return self.gainloss*(self.totalPurchasePrice-self.commissionToBuy)-(self.totalPurchasePrice-self.commissionToBuy)
    def GetTicker(self):
        return self.ticker
    def GetPurchaseDate(self):
        return  self.purchaseDate.strftime('%Y-%m-%d')
    def GetTotalPurchasePrice(self):
        return self.totalPurchasePrice

#using the miniStock is inefficient bc you are repeatedly going out to the web to pull the quotes. You really want to use the Stock Objects, pass them in and then do the comparison.
class ComparisonStock:
    def __init__(self,stockdata1,stockdata2):
#create two ministock objects  
#is there a better way to utilize objects? init the object and pass it in and copy or deepcopy it? Hmm that doesn't seem right bc then there is the original hanging out there that is just taking up space.
        self.miniStock1=MiniStock(stockdata1)
        self.miniStock2=MiniStock(stockdata2)
    def Header(self):
        """
        """
        print("%5s %s %s %s %s %s %s %s" % ("buy date","init inv","tickr","gain/loss","tickr","gain/loss","value1","value2" ))
    def printComparison(self):
        """
        
        """
        self.Header()
        print("%5s %6.2f %5s"  % (self.miniStock1.GetPurchaseDate(),self.miniStock1.GetTotalPurchasePrice(),self.miniStock1.GetTicker()),end=' ')
        ColorCode10pt2fRelative(self.miniStock1.GetGainLoss(),1)
        DefaultColorCoding() 
        print(" %5s " % (self.miniStock2.GetTicker()), end=' ')
        ColorCode10pt2fRelative(self.miniStock2.GetGainLoss(),1)
        DefaultColorCoding() 
        self.printBest()

    def printBest(self):
        """
        """
        total1=self.miniStock1.GetTotalPurchasePrice()*self.miniStock1.GetGainLoss()
        total2=self.miniStock1.GetTotalPurchasePrice()*self.miniStock2.GetGainLoss()
        ColorCode10pt2fRelative(total1,total2)
        DefaultColorCoding()
        print( " vs ", end= ' ')
        ColorCode10pt2fRelative(total2,total1)
        DefaultColorCoding()
        print("")

def printCompareHeader():
    print("  buy date  InitInv  tickr  gain/loss     tickr      gain/loss       value1            value2" )

class CompareStock:
    """
    Class to compare two stocks performance and output a small summary comparison
    """
    def __init__(self,stockdata1,stockdata2):
        """
        #create two ministock objects  
        #is there a better way to utilize objects? init the object and pass it in and copy or deepcopy it? Hmm that doesn't seem right bc then there is the original hanging out there that is just taking up space.
        """
        self.Stock1=stockdata1
        self.Stock2=stockdata2

    def printComparison(self):
        """
        Prints purchase date, total purchase price, ticker of stock1 , gain/loss of stock 1, ticker of stock 2, gain/loss of stock 2, and then outputs stock1 vs stock2 values and highlights which one would've produced better gains.
        """
        print("%5s %6.2f %5s"  % (self.Stock1.GetPurchaseDateYYYY_MM_DDFormatted(),self.Stock1.GetTotalPurchasePrice(),self.Stock1.GetTicker()),end=' ')
        ColorCode10pt2fRelative(self.Stock1.GetGainLoss(),1)
        DefaultColorCoding() 
        print(" %5s " % (self.Stock2.GetTicker()), end=' ')
        ColorCode10pt2fRelative(self.Stock2.GetGainLoss(),1)
        DefaultColorCoding() 
        self.printBest()

    def printBest(self):
        """
        Compare two stocks gains/losses and output their values color coding the better investment of the two.
        """
        total1=self.Stock1.GetTotalPurchasePrice()*self.Stock1.GetGainLoss()
        total2=self.Stock1.GetTotalPurchasePrice()*self.Stock2.GetGainLoss()
        ColorCode10pt2fRelative(total1,total2)
        DefaultColorCoding()
        print( " vs ", end= ' ')
        ColorCode10pt2fRelative(total2,total1)
        DefaultColorCoding()
        print("")
        
    
class Stock:
    """
    Base Stock class to use for calculating returns, gains losses etc.
    "Stock" is a bit of a misnomer for this class as it really is meant to represent a transaction involving a single security but multiple shares, including recording any fees in the transaction
    """
    currentshareprice=0.0
    percentgainloss=0.0
    pricegainloss=0.0
    annualizedgainloss=0.0
    shareopenprice=0.0
    shareprevcloseprice=0.0
    taxbracket=0 
    filingstatus=""
    def __init__(self, data): #ticker,sharequantity,totalpurchaseprice,purchasedateyear,purchasedatemonth,purchasedateday,commission_to_buy,commission_to_sell):
        """
        Stock Constructor
        """
        self.ticker=data["ticker"]
        self.sharequantity=float(data["shares"]) #allow for partial shares, useful for mutual funds, and reverse splits
        self.totalpurchaseprice=float(data["totalPurchasePrice"])
        temp=data["purchaseDate"].split('/')
        self.purchasedate=datetime.datetime(int(temp[2]),int(temp[0]),int(temp[1]))
        if data["commissionToBuy"]!="":
            self.commission_to_buy=float(data["commissionToBuy"])
        else:
            self.commission_to_buy=0
        if data["commissionToSell"]!="":
            self.commission_to_sell=float(data["commissionToSell"])
        else:
            self.commission_to_sell=0
        self.getSharePrice()
        self.dollarGain=self.dollarGain_func()
        self.percentGain=self.percentGain_func()
        self.annualizedReturn=self.annualizedReturn_func()
        self.getTaxBracket_func()
    def tickerLink(self):
        """
        Output a html link to the ticker's yahoo 1 yr chart
        """
        output="<a href=\"http://finance.yahoo.com/echarts?s="+self.ticker+"+Interactive#symbol="+self.ticker+";range=1y\">"+self.ticker+"</a>"
        return output

        #number formatting documentation: http://docs.python.org/3.3/library/string.html#format-string-syntax , see the answer further down for specifying more than one format option http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x
    def htmlTableRowOutput(self):
        """
        Create an html table row of the 17 fields we report
        """
        separator="</td><td>"
        output="<tr><td> {0} {1} {2} {1} {3} {1} {4} {1} {5:,.2f} {1} {6} {1} {7:,.2f} {1} {8:,.2f} {1} {9:,.2f} {1} {10:,.2f} {1} {11} {1} {12:,.2f} {1} {13:,.2f} {1} {14:,.2f} {1} {15:,.2f} {1} {16:} {1} {17:,.2f}</td></tr>".format(
self.tickerLink(), 
separator, 
htmlTableColorCode(self.dollarGain), 
htmlTableColorCode(self.annualizedReturn), 
htmlTableColorCode(self.percentGain_func()), 
self.currentWorth_func(), 
htmlTableColorCode(self.dailyChange_func()), 
self.currentshareprice, 
self.shareprevcloseprice, 
self.share52wkhigh, 
self.share52wklow, 
self.trend, 
self.stockSaleTakeHome_func(), 
self.stockSaleTaxes_func(), 
self.stockpriceDiscountedForTaxes_func(), 
self.FiftyTwoWeekHighLowFactor(), 
htmlTableComparisonColorCode(self.resultsIfInvestedInSP500(),self.currentWorth_func()  ),
self.yearsSincePurchase() )
            # output="<tr><td>"+self.tickerLink()+separator + \
            # htmlTableColorCode(self.dollarGain)+ separator + \
            # htmlTableColorCode(self.annualizedReturn)+ separator + \
            # htmlTableColorCode(self.percentGain_func())+ separator + \
            # str(self.currentWorth_func())+ separator + \
            # htmlTableColorCode(self.dailyChange_func()) + separator + \
            # str(self.currentshareprice)+ separator +str(self.shareprevcloseprice)+ separator + \
            # str(self.share52wkhigh)+ separator +str(self.share52wklow)+ separator +str(self.trend)+ separator + \
            # str(self.stockSaleTakeHome_func())+ separator +str(self.stockSaleTaxes_func())+ separator +str(self.stockpriceDiscountedForTaxes_func())+ separator +str(self.FiftyTwoWeekHighLowFactor())+ separator + \
            # str(self.resultsIfInvestedInSP500()) + separator + \
            # str(self.yearsSincePurchase()) + \
            # "</td></tr>"
        return output

    def getDictionary(self):
        """
        
        """
        output={}
        output['Commission To Buy']=self.commission_to_buy
        output['Commission To Sell']=self.commission_to_sell
        output['Share Price']=self.currentshareprice
        output['Ticker']=self.ticker
        output['Purchase Date']=self.purchasedate
        output['Percent Gain']=self.percentGain
        output['Dollar Gain']=self.dollarGain
        output['Annualized Return']=self.annualizedReturn
        output['TimeStamp']=datetime.datetime.now() #.utcnow()# http://pleac.sourceforge.net/pleac_python/datesandtimes.html
        return output
            
    def getTaxBracket_func(self):
        """
        Read in the tax bracket and filing status from the given file 
        these fields are then used for 
        """
        input=open(os.path.expanduser("TaxBracket.txt")) #~/Git/PythonStockTracker/TaxBracket.txt")) #the os.path.expanduser is unnecessary unless you are using the ~ to denote the user's home path
        for line in input:
            data=""
            if line.strip(): #skip blank lines
                if line[0]!='#': #skip comments
                    data=line[:-1].split(',')
                    self.taxbracket=int(data[0])
                    self.filingstatus=data[1]

    def GetTicker(self):
        return self.ticker
    def GetGainLoss(self):
        return self.percentGainLoss_func()
    def GetTotalPurchasePrice(self):
        return self.totalpurchaseprice
    def GetPurchaseDateYYYY_MM_DDFormatted(self):
        return self.purchasedate.strftime('%Y-%m-%d')
    def GetPurchaseDate(self):
        return self.purchasedate
    def GetStockData(self):
        print("get stock data")


    def percentGain_func(self): 
        return (self.sharequantity*self.currentshareprice-self.totalpurchaseprice)/self.totalpurchaseprice
    def percentGainLoss_func(self): #not sure what a good term for this is ROI?
        return (self.sharequantity*self.currentshareprice)/self.totalpurchaseprice
    def dollarGain_func(self):
        return float(self.sharequantity*self.currentshareprice-self.totalpurchaseprice)

    def annualizedReturn_func(self):
        """
        Calculate the annualized rate of return for this investment
        
        """
        ARR=0
        if (self.yearsSincePurchase() > 0):
            ARR=(((self.dollarGain/self.totalpurchaseprice+1)**(1/self.yearsSincePurchase()) -1 ) *100)
        return ARR #(((self.dollarGain/self.totalpurchaseprice+1)**(1/self.yearsSincePurchase()) -1 ) *100)

    def stockSaleTaxes_func(self): 
        """
        calculate amount you would pay in taxes on your stock sale, taxed only on gains!
        """
        if self.currentWorth_func()>self.totalpurchaseprice-self.commission_to_buy:
            output=(self.currentWorth_func()-self.totalpurchaseprice+self.commission_to_buy)*self.taxRate_func()
        else:
            output=0 #we're in the red. Not sure just yet how the taxes apply here
        return output

    def stockSaleTakeHome_func(self): 
        """
        calculate amount you would receive after taxes on your stock sale
        """
        if self.currentWorth_func()>self.totalpurchaseprice-self.commission_to_buy:
            output=self.currentWorth_func()-(self.currentWorth_func()-self.totalpurchaseprice+self.commission_to_buy)*self.taxRate_func() 
        else:
            output=0 #we're in the red. Not sure just yet how the taxes apply here
        return output

    def stockpriceDiscountedForTaxes_func(self): 
        """
        the effective price the stock would appear when selling, taking into acct deductions for taxes: 
        e.g. a $120 stock bought for $20 at a 38% tax rate would appear as a $82 stock 
        $100 profit is turned into $62 profit due to taxes.
        -> (120-20)*(1-.38)+20=82
        
        if we are in a tax loss situation we calculate the share purchase price and mark with a negative sign to denote we are under water.
        
        """
        discountedPrice= (self.currentWorth_func()-(self.currentWorth_func()-(self.totalpurchaseprice-self.commission_to_buy))*self.taxRate_func())/self.sharequantity #this math is correct. I tried to simplify by writing it out and simplifying the equation, thats why it may look goofy
        if self.currentWorth_func()<self.totalpurchaseprice-self.commission_to_buy:  #if our shares are worth less we return the share purchase  price and mark it as such with a negative share value
            discountedPrice=-(self.totalpurchaseprice-self.commission_to_buy)/self.sharequantity
        return discountedPrice 

    def oneMinusTaxRate_func(self):
        """
        returns the percentage amount of the profit that you would see based on the appropriate ST or LT tax rate
        i.e.if the investment was held less than a year (short term capital gains) at a 35% tax rate, you would receive only 65% of the profit
        """
        if self.yearsSincePurchase()>1:
            taxrate=(100-self.calculateLongTermCapitalGains_func())/100  #<-- due to pythons untyped variables this is evaluated as an int even when wrapped in float()
            taxrate=(100-self.calculateLongTermCapitalGains_func())/100.0 #<-- turning the denominator in a float types the whole thing as a float
        else:
                taxrate=(100-self.calculateShortTermCapitalGains_func())/100.0
        return taxrate

    def taxRate_func(self): 
        """
            
        """
        if self.yearsSincePurchase()>1:
            taxrate=(self.calculateLongTermCapitalGains_func())/100.0
        else:
            taxrate=(self.calculateShortTermCapitalGains_func())/100.0
        return taxrate

    def calculateLongTermCapitalGains_func(self):
        """

        """
        taxlist=[0,15]
        if self.taxbracket in taxlist:
            return 0
        else:
            return 15

    def calculateShortTermCapitalGains_func(self):
        return self.taxbracket
    def currentWorth_func(self):
        return self.sharequantity*self.currentshareprice 
    def dailyChange_func(self):
        return   self.sharequantity*(self.currentshareprice - self.shareprevcloseprice)
    def PrintData(self):
        """
        Not Used
        """
        print("-----------------=======================-----------------")
        print(("Ticker:"+self.ticker))
        print(("Shares:"+str(self.sharequantity)))
        print(("Total Purchase Price:"+str(self.totalpurchaseprice)))
        print(("Purchase Date:"+str(self.purchasedate)))
        print(("Dollar Gain:"+str(self.dollarGain)))
        print(("Percent Gain:"+str(self.percentGain)))
        print(("Annualized Return:"+str(self.annualizedReturn)))
        print(("Current Value:"+str(self.sharequantity*self.currentshareprice)))
        print(("Current Share Price:"+str(self.currentshareprice)))
        print(("Current Open  Price:"+str(self.shareopenprice)))
        print(("Current 52 Week High:"+str(self.share52wkhigh)))
        print(("Current 52 Week Low:"+str(self.share52wklow)))
        print(("Current Trend:"+self.trend))
        
    def FiftyTwoWeekHighLowFactor(self):
        """
        Calculate, as a percentage, where in the 52wk range the current price lies.
        e.g. 52wk range: $200-$100, current price: $175, therefore the current price is 75% of the way to the high
        """
        if self.share52wkhigh!=0 and self.share52wklow!=0:
            return (self.currentshareprice-self.share52wklow)/(self.share52wkhigh-self.share52wklow)
        else:
            return 0
            
 
    def PrintCompact2(self):
        """
        Not Used
        """
        print((" %8s %8.2f %8.2f %8.2f %8.2f %8.2f %8.2f"  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice,self.sharequantity*(self.currentshareprice - self.shareprevcloseprice),self.currentshareprice,self.shareprevcloseprice)))
            
    def PrintForTxtMessage(self):
        message="Ticker: %8s $+-: %8.2f AnnlRet: %8.2f Worth:%8.2f DayChange:%8.2f"  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice,self.sharequantity*(self.currentshareprice - self.shareprevcloseprice  ))
        return  message
    def PrintCompact(self):
        """
        Not Used
        """
        print((" %8s %8.2f %8.2f %8.2f "  % (self.ticker,self.dollarGain,self.annualizedReturn,self.currentWorth_func())))
                
    def PrintColorized(self):
        """
        Not Used
        """
        print(("%7s"  % (self.ticker)), end=' ')
        ColorCode10pt2f(self.dollarGain)
        ColorCode10pt2f(self.annualizedReturn)
        ColorCode10pt2f(self.percentGain_func())
        print(("\033[49m \033[39m"), end=' ')
        print(("%10.2f" % (self.currentWorth_func())), end=' ') #self.sharequantity*self.currentshareprice )),
        ColorCode10pt2f(self.dailyChange_func()) #self.sharequantity*(self.currentshareprice - self.shareprevcloseprice)) #if today was an 'up' or 'down'  day for the stock let that color coding propagate to the next two fields
        print(("%10.2f %10.2f" %(self.currentshareprice,self.shareprevcloseprice)), end=' ')
        print(("\033[49m \033[39m"), end=' ') #reset color to default
        print(("%10.2f %10.2f %6s" %(self.share52wkhigh,self.share52wklow,self.trend)))

    def PrintColorized2(self):
        """
        Not Used
        """
        print(("%7s"  % (self.ticker)), end=' ')
        ColorCode10pt2f(self.dollarGain)
        ColorCode10pt2f(self.annualizedReturn)
        ColorCode10pt2f(self.percentGain_func())
        print(("\033[49m \033[39m"), end=' ')
        print(("%10.2f" % (self.currentWorth_func())), end=' ') #self.sharequantity*self.currentshareprice )),
        ColorCode10pt2f(self.dailyChange_func()) #self.sharequantity*(self.currentshareprice - self.shareprevcloseprice)) #if today was an 'up' or 'down'  day for the stock let that color coding propagate to the next two fields
        print(("%10.2f %10.2f" %(self.currentshareprice,self.shareprevcloseprice)), end=' ')
        print(("\033[49m \033[39m"), end=' ') #reset color to default
        print(("%10.2f %10.2f %6s" %(self.share52wkhigh,self.share52wklow,self.trend)), end=' ')
        print(("%10.2f %10.2f %10.2f %10.2f" %(self.stockSaleTakeHome_func(),self.stockSaleTaxes_func(),self.stockpriceDiscountedForTaxes_func(),self.FiftyTwoWeekHighLowFactor())))

    def PrintColorized3(self):
        """
        Print out dollar gain, annualized rate of return, percent gain/loss, current investment worth, daily change of investment, current share price, prev close of share price, 52 wk high, 52 wk low, trend, proceeds you would see if sold immediately, taxes due on such an immediate sale, adjusted stock price taking into account taxes , 52 week high low factor, theoretical results if invested in the SP500, years since purchased
        """
        print(("%7s"  % (self.ticker)), end=' ')
        ColorCode10pt2f(self.dollarGain)
        ColorCode10pt2f(self.annualizedReturn)
        ColorCode10pt2f(self.percentGain_func())
        print(("\033[49m \033[39m"), end=' ')
        print(("%10.2f" % (self.currentWorth_func())), end=' ') #self.sharequantity*self.currentshareprice )),
        ColorCode10pt2f(self.dailyChange_func()) #self.sharequantity*(self.currentshareprice - self.shareprevcloseprice)) #if today was an 'up' or 'down'  day for the stock let that color coding propagate to the next two fields
        print(("%10.2f %10.2f" %(self.currentshareprice,self.shareprevcloseprice)), end=' ')
        print(("\033[49m \033[39m"), end=' ') #reset color to default
        print(("%10.2f %10.2f %6s" %(self.share52wkhigh,self.share52wklow,self.trend)), end=' ')
        print(("%10.2f %10.2f %10.2f %10.2f" %(self.stockSaleTakeHome_func(),self.stockSaleTaxes_func(),self.stockpriceDiscountedForTaxes_func(),self.FiftyTwoWeekHighLowFactor())),end=' ')
        print(("%10.2f" %( self.resultsIfInvestedInSP500() )), end=' ')
        print(("%2.1f" %( self.yearsSincePurchase() )))

        #NOTE:
        #I could make these print functions more multipurpose by defining a function that outputs a new line and otherwise you prevent the newline from being added. Then just pick and choose which statements you want printed.
        #or have a check as to print this field or not.
        
    def getSharePrice(self):
        """
        Get share price for given ticker
        if the ticker is the TRowePrice prime reserve, then we report that as ~$1 a share since that is what prime reserves do and it lets the calculations work to give a still decent account of the portfolio with PRRXX in it
        the date goes month(jan=0) day year
        
        we actually need to get the prev close to compute gain for the day. Wall Street doesn't compute the gain from the open, but from prev close
        """
        url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1opwt7'
        if (self.ticker=="prrxx"):
            self.shareopenprice=1.0
            self.share52wklow=1.000001
            self.share52wkhigh=1.0
            self.trend="===="
        else:
            days = str(urllib.request.urlopen(url).read() , encoding='utf8')  #lines()
            data = days[:-2].split(',') 
            if float(data[0])==0.0:
                print("Uhh bad stock ticker: %7s" % self.ticker)
            self.currentshareprice=float(data[0])
            if data[1]!="N/A": #not sure I even need the share open price. I don't do anything with it.
                self.shareopenprice=float(data[1])
            self.shareprevcloseprice=float(data[2])
            if data[3]!="\"N/A - N/A\"":
                temp=data[3].split(" - ")
                self.share52wklow=float(temp[0][1:])
                self.share52wkhigh=float(temp[1][:-1])
                self.trend=data[4][7:13]
            else:
                self.share52wklow=0.0001
                self.share52wkhigh=0.0002
                self.trend="N/A"





                """
                create a global dict of dates:prices for SP500
                check the list to see if that date's price has all ready been retrieved.
                if not retrieve the price for that day and add it to the list
                
                compute the ARR for the time period X until today
                """

    def resultsIfInvestedInSP500(self):
        """
        """
        avgAnnualReturn=1.10 #10% annual return
        #            print(self.yearsSincePurchase(),self.totalpurchaseprice,avgAnnualReturn)
        return (self.totalpurchaseprice*(avgAnnualReturn**self.yearsSincePurchase())) #I'm not sure if this is completely accurate due to partial years etc. and avg daily rates possibly being diff. need to research this.
        
    def yearsSincePurchase(self):
        """
        Determine the time period, in fractional years, since the investment was made
        is there an easier way to do this with the built in time functions?-->doesn't appear to be : http://www.python-forum.org/pythonforum/viewtopic.php?f=3&t=4553  http://stackoverflow.com/questions/4436957/pythonic-difference-between-two-dates-in-years http://stackoverflow.com/questions/6451655/python-how-to-convert-datetime-dates-to-decimal-years http://www.google.com/search?q=fraction+years+between+dates+python&oq=fraction+years+between+dates+python&sugexp=chrome,mod=0&sourceid=chrome&ie=UTF-8
        """
        now=datetime.datetime.now()
        daysElapsed=(now-self.purchasedate).days
        yearsElapsed=now.year-self.purchasedate.year
        daysCalc=datetime.datetime(now.year,self.purchasedate.month,self.purchasedate.day)
        days2=(now-daysCalc).days
        if days2 <0: #the case when trying to do june 6 2012 -Oct 8 2011, so have to subtract a year 
            yearsElapsed=yearsElapsed-1
            daysCalc=datetime.datetime(now.year-1,self.purchasedate.month,self.purchasedate.day)
            days2=(now-daysCalc).days
                
        daysinyear=365.0 #force to be float so the division works as we would expect
        yr=now.year
        if isLeapYear(yr): #now.year):
            daysinyear+=1
        daysDiff=(days2/daysinyear)
        return yearsElapsed+daysDiff

    def JSON(self):
        """
        Output Stock data as a json object
        """
        data=json.dumps({
            "Ticker":self.ticker,
            "Shares":str(self.sharequantity),
            "Total Purchase Price":str(self.totalpurchaseprice),
            "Purchase Date":str(self.purchasedate),
            "Dollar Gain":str(self.dollarGain),
            "Percent Gain":str(self.percentGain),
            "Annualized Return":str(self.annualizedReturn),
            "Current Value":str(self.sharequantity*self.currentshareprice),
            "Current Share Price":str(self.currentshareprice),
            "Current Open  Price":str(self.shareopenprice),
            "Current 52 Week High":str(self.share52wkhigh),
            "Current 52 Week Low":str(self.share52wklow),
            "Current Trend":self.trend
            })
        return data

        #just use FiftyTwoWeekHighLowFactor
        # def get52WeekHighCheck(self):
        #     return (self.currentshareprice-self.share52wklow) / (self.share52wkhigh-self.share52wklow);

        # def get52WeekLowCheck(self):
        #     return (self.currentshareprice - self.share52wkhigh ) / self.share52wkhigh;

            


def StockTable(inputfilename):
    """
    #This methoad traverses a portfolio and outputs the performance of each stock in the portfolio
    #as well as overall performance.
    """
    input=open(inputfilename)
    data_string=json.load(input)
    emailReportMsg=""
    htmlOutput=" "
    jsonOutput="{ \"portfolio\":["
    for portfolio in data_string["portfolio"]:
        if portfolio["display"] == "yes":
            jsonOutput+="{\"portfolioname\":\"" + portfolio["portfolioName"]+"\", \"portfolioStocks\":["
            print('==================----------',portfolio["portfolioName"],'----------==================')
            DefaultColorCoding()
            PrintHeader2()
            cumulative=Accumulator()
            emailReportMsg+=portfolio["portfolioName"]
            for data in portfolio["portfolioStocks"]:
                stock=Stock(data)
                cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain,stock.dailyChange_func() ,stock.currentWorth_func() )
                stock.PrintColorized3() #includes theoretical "what if" invested in SP500 instead
                message=stock.PrintForTxtMessage()
                emailReportMsg+=stock.JSON()
                jsonOutput+=stock.JSON()+"," 
            jsonOutput=jsonOutput.rstrip(',') 
            jsonOutput+="],"
            jsonOutput+="\n" 
            jsonOutput+="\"cumulative Result\":"+cumulative.JSONify()+"}," #will need to get rid of the last trailing , 
            emailReportMsg+=cumulative.JSONify()+",\n"
            cumulative.Print()
            DefaultColorCoding()
    jsonOutput=jsonOutput.rstrip(',') 
    jsonOutput+="] }"
    input.close()
    output=open("jsonoutput.txt",'w')
    output.write(jsonOutput)
    output.close()
    return stock.getDictionary() #outputlist #emailReportMsg

class HTMLTable:
    """
    This methoad traverses a portfolio and outputs the performance of each stock in the portfolio
    as well as overall performance.
    """
    def __init__(self,inputfilename):
        input=open(inputfilename)
        portfolioTabsList=[]
        portfolioStockDataList=[]
        portfolioTabContentsList=[]
        filename=inputfilename.split('.')
        outputfilename=filename[0]+".html"
        data_string=json.load(input)
        htmlOutput=" "
        for portfolio in data_string["portfolio"]:
            if portfolio["display"] == "yes":
                portfolioName=portfolio["portfolioName"]
                portfolioTabsList.append(portfolio["portfolioName"])
                cumulative=Accumulator()
                for data in portfolio["portfolioStocks"]:
                    stock=Stock(data)
                    cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain,stock.dailyChange_func() ,stock.currentWorth_func() )
                    portfolioStockDataList.append(stock.htmlTableRowOutput())
                portfolioTabContentsList.append(createPortfolioTable(portfolioName,portfolioStockDataList,cumulative.HTMLTableOutput())) 
            portfolioStockDataList=[] #clear the list for the next portfolio
        input.close()
        output=open(outputfilename,'w')
        output.write(createHTMLOutput(portfolioTabsList,portfolioTabContentsList))
        output.close()
        print("Output written to ",outputfilename,".")
        

def createPortfolioTable(name,dataList,cumulativeData):
    """
    Given a portfolio name, a list of stock data , and a list of cumulative portfolio data, create an html table to display the data
    """
    startText='<table border="2"><caption>'
    output=startText+name+"</caption>"
    header="""<tr><th>Ticker</th><th>
   $ gain</th><th>
    Ann %</th><th>
    % gain</th><th>
    Curr Worth</th><th>
    Today chg $</th><th>
    Curr Price</th><th>
    Prev Close</th><th>
    52 High</th><th>     
    52 Low </th><th>
    Trend</th><th>
    Sale Tk Home</th><th> 
    Sale Taxes</th><th> 
    Disc4Taxes</th><th>
    HiLoPct</th><th>
    Value if invested in SP500</th><th> 
    Years Held </th></tr>"""
    output+=header
    for item in dataList:
        output+=item
    output+=cumulativeData+'</table>'
    return output

def jqueryUITabs(tabList):
    """
    Given a list of portfolio names, create a set of tabs for jqueryUI tab usage
    """
    startText="""<div id="tabs"> 
    <ul>"""
    endText='</ul>'
    itemStart='<li><a href="#tabs-'
    itemEnd='</a></li>'
    output=startText
    for counter,item in enumerate(tabList):
        output+=itemStart+str(counter)+"\">"+item+itemEnd
    output+=endText
    return output

def tabContent(tabList):
    """
    Given a list of html elements, create the tab contents to be displayed with the jqueryUI tabs.
    """
    start='<div id="tabs">'
    startText='<div id="tabs-'
    endText='</div>'
    output=start
    for counter,item in enumerate(tabList):
        output+=startText+str(counter)+"\">"+item+endText
    return output
    
def createHTMLOutput(portfolioNameList,portfolioContentList):
    """
    create an html webpage from a list of portfolio names, and their performance data in html
    """
    start="""<html lang="en"> 
    <head>
    <meta charset="utf-8" />
    <title>jQuery UI Tabs - Default functionality</title>
    <link rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
    <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
    <script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
    <link rel="stylesheet" href="/resources/demos/style.css" />
    <script>
    $(function() {
    $( "#tabs" ).tabs();
    });
    </script>
    <style type="text/css">
    .negative1 {color:red }
    .negative {background-color:red }
    .positive1 {color:green }
    .positive {background-color:green }
    td {text-align:right}
    </style>
    </head>
    <body>
    """
    end='</div></body></html>'
    tabs=jqueryUITabs(portfolioNameList)
    content=tabContent(portfolioContentList)
    output=start+tabs+content+end
    return output
        

def MongoStockTable_Old(inputfilename):
    """
    """
    input=open(inputfilename)
    outputlist=[]
    data_string=json.load(input)
    print("I need to create one large dictionary of the portfolios and their contents")
    for portfolio in data_string["portfolio"]:
        if portfolio["display"] == "yes":
            cumulative=Accumulator()
            for data in portfolio["portfolioStocks"]:
                stock=Stock(data)
                cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain,stock.dailyChange_func() ,stock.currentWorth_func() )
                message=stock.PrintForTxtMessage()
                MongoSave(stock.getDictionary())
    input.close()

def MongoStockTable(inputfilename):
    """
    create json output for saving in a mongo db
    """
    input=open(inputfilename)
    data_string=json.load(input)
    jsonOutput="{ \"portfolio\":["
    for portfolio in data_string["portfolio"]:
        if portfolio["display"] == "yes":
            jsonOutput+="{\"portfolioname\":\"" + portfolio["portfolioName"]+"\", \"portfolioStocks\":["
            cumulative=Accumulator()
            for data in portfolio["portfolioStocks"]:
                stock=Stock(data)
                cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain,stock.dailyChange_func() ,stock.currentWorth_func() )
                jsonOutput+=stock.JSON()+"," 
            jsonOutput=jsonOutput.rstrip(',') # remove that trailing extraneous ,   [:-1]
            jsonOutput+="],"
            jsonOutput+="\n" 
            jsonOutput+="\"cumulative Result\":"+cumulative.JSONify()+"}," 
    jsonOutput=jsonOutput.rstrip(',') 
    jsonOutput+="] }"
    MongoSave(ast.literal_eval(jsonOutput))
    input.close()


def MongoSave(message):
    """
    Save the provided message into the AllPorfolios table of the local mongo db instance.
    """
    client = pymongo.MongoClient("localhost",27017)
    db = client.PortfolioTracker
    db.AllPortfolios.save(message)#this must be a dictionary for proper insertion http://docs.python.org/2/tutorial/datastructures.html#dictionaries
#http://docs.mongodb.org/manual/tutorial/getting-started-with-the-mongo-shell/

def Alert(inputfilename,alertPercent):
    """
    
    #better algo, compile list of uni ... um never mind. I was going to say to compile list of unique stocks and only compute 1x for each stock, but depending on when you bought, it may be a winner and loser.
    """
    input=open(inputfilename)
    data_string=json.load(input)
    print('The following stocks have dropped below your threshold.')
    for portfolio in data_string["portfolio"]:
        print('==================----------',portfolio["portfolioName"],'----------==================')
        for data in portfolio["portfolioStocks"]:
            stock=Stock(data)
            if stock.GetGainLoss()<(1-alertPercent):
                print(stock.ticker.upper())
#            else:
#                print(stock.GetGainLoss(),stock.ticker,(1-alertPercent))

    input.close()


def ComparePortfolio(inputfilename):
    """
    this method  traverses a portfolio and compares the performance of the two stocks against each other.
    the first stock's purchase date is used to perform the benchmark.
    the performance of each stock from that purchase date is calculated
    the print out shows each stock's return from the purchase data as welll as what that initial investment is and what it 
    would've turned into if the second stock was purchased instead.
    
    """
    input=open(inputfilename)
    data_string=json.load(input)
 #   stockCollection=[]
    stockz=[]
    for portfolio in data_string["portfolio"]:
        print('==================----------',portfolio["portfolioName"],'----------==================')
        for stock in portfolio["portfolioStocks"]:
#            stockCollection.append(stock)#portfolio["portfolioStocks"][i])
            stockz.append(Stock(stock))
        # for i in (range(len(stockCollection)-1)): #subtract 1 because we don't want to comare ele[max] to ele[max]
        #     for k in (range(i+1,len(stockCollection))):
        #         print(i,k)

# #this isn't the correct looping pattern because we want to see how X would've faired from Y's starting point and not just the other way around.
#         for i in range(len(stockCollection)-1):
#             for k in (range(i+1,len(stockCollection))):
# #                print(i,k)
#                 compare=ComparisonStock(portfolio["portfolioStocks"][i],portfolio["portfolioStocks"][k])
#                 compare.printComparison()
#             print('-----')

# #this is the correct looping pattern bc we want to not compare each stock to itself but to all others in the list.
# this is the older MUCH slower version with redundant calls to yahoo which really bogged things down.
#         print(len(stockCollection))
#         for i in range(len(stockCollection)):
#             for k in range(len(stockCollection)):
#                 if i!=k:
#                     #print(i,k,stockCollection[i]["ticker"],stockCollection[k]["ticker"])
#                     compare=ComparisonStock(portfolio["portfolioStocks"][i],portfolio["portfolioStocks"][k])
#                     compare.printComparison()
                    
#             print('---')

#this is the correct looping pattern bc we want to not compare each stock to itself but to all others in the list.
#        print(len(stockz))
        for i in range(len(stockz)):
            printCompareHeader()
            for k in range(len(stockz)):
                if i!=k:
                    #print(i,k,stockzCollection[i]["ticker"],stockCollection[k]["ticker"])
                    compare=CompareStock(stockz[i],stockz[k])
                    compare.printComparison()
            print('') #---')
        stockCollection=[] #reset the stock collection
        stockz=[]
    input.close()

#TODO: create Portfolio object and have a total for the entire portfolio
#todo: trend line of +-+-++ for last few days worth of trading,
#generic line for an index. as comparison

def usage():
    print("python StockTrackerJSON  [ -c/--comparison, -i/--input=portfolio.json -s/--stocktable -e/--email -w/--web-html]")
    print("-a/--alert=X Only output those stocks whose value has dropped below X % of the purchase price.")
    print("-c/--comparison Output performance comparing each stock to all the others in the portfolio")
    print("-i/--input=portfolio.json")
    print("-s/--stocktable Output the stock table ")
    print("-e/--email=joe.schmoe@email.org Email the results to user joe.schmoe@email.org")
    print("-m/--mongo Output data to local MongoDB instance AllPortfolios table")
    print("-w/--web-html output the data in a webpage name Portfolioname.html e.g. AllPortfolios.json -> AllPortfolios.html")
    print("python StockTrackerJSON -iPortfolio.json -c -s")

"""
############ Main 
"""

#use ncurses, ansi color codes

from  textwrap import TextWrapper
wrapper =TextWrapper()
wrapper.width=190 #set text wrapping width manually otherwise if drag terminal to full width python doesn't write text out the full width

import getopt 
import sys


comparisonflag=False
stocktableflag=False
alertflag=False
alertPercent=0.8
destinationemail="foo.bar@example.com"
mongoflag=False
htmltableflag=False
print(sys.argv[1:])
#pretty much straight from : http://docs.python.org/release/3.1.5/library/getopt.html
#took me a while to catch that for py3k that you don't need the leading -- for the long options
#sadly optional options aren't allowed. says it in the docs :( http://docs.python.org/3.3/library/getopt.html
try:
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'a:e:csi:mw', ['alert=',
                                                                        'compare',
                                                                        'stocktable',
                                                                        'input=',
                                                                        'email=',
                                                                        'mongo',
                                                                        'web-html-table'
                                                                ])
except getopt.GetoptError as err:
    # print help information and exit:                                                                        
    print( str(err)) # will print something like "option -a not recognized"                                         
    usage()                                                                                                  
    sys.exit(2)

for opt, arg in options:
    if opt in ('-c', '--compare'):
        comparisonflag=True
    elif opt in ('-s', '--stocktable'):
        stocktableflag=True
    elif opt in ('-w', '--web-html-table'):
        htmltableflag=True
    elif opt in ('-m', '--mongo'):
        mongoflag=True
    elif opt in ('-i', '--input'):
        inputfilename=arg
    elif opt in ('-e', '--email'):
        destinationemail=arg
    elif opt in ('-a', '--alert'): #check for stocks where loss is > 8 %
        alertflag=True
        try:
            alertPercent=float(arg) #will it break if an opt isn't specified?
        except ValueError:
            alertPercent=8
        if alertPercent > 1:
            alertPercent=alertPercent/100;
    else:
        assert False, "unhandled option"

# #import os.path
# #loop over command line args
# sysargvlength=len(sys.argv)
# print('sysargv length',sysargvlength,'sysargv',sys.argv)
# #element 0 is the script name, rest of the elements should be files.
# i=1
# #although by using a .json file we intend to eliminate specifying multiple files on the command line.
# while i < sysargvlength:
# if sysargvlength>1 and os.path.isfile(sys.argv[i]):
#     inputfilename=sys.argv[i]
# i+=1
usage()
PrintBanner(inputfilename)

#this is super inefficient. I should go out and construct the data for each stock / portfolio and then run the stats, using those objects. I shouldn't go out and get the yahoo data for each function
#TODO make this efficient. eliminate the unnecessary slow calls to yahoo
if stocktableflag:
    StockTable(inputfilename)
if comparisonflag:
    ComparePortfolio(inputfilename)
if alertflag:
    Alert(inputfilename,alertPercent)
if htmltableflag:
    HTMLTable(inputfilename)
if mongoflag:
    MongoStockTable(inputfilename)
#    MongoSave(StockTable(inputfilename))#.JSONify())
#    MongoSave("{ 'name':'bob', 'hair':'bald'}")#.JSONify())
print("") #otherwise the prompt isn't on a new line

