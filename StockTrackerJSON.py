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

#class StockList:
#    def __init__(self,
def DefaultColorCoding():
    print(("\033[49m \033[39m "), end=' ') #set to default color coding, suppress newline

def isLeapYear(year):
    leapyear=0
    if year%4==0:
        leapyer=1
    return leapyear

def getSharePrices(tickerlist):
#tickerlist should be a set of ticker symbols with '+' in between
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %tickerlist + '&f=l1'
#            url = 'http://download.finance.yahoo.com/d/quotes.csv?s=AAPL&f=l1' l1=>last trade without time.
    days = str( urllib.request.urlopen(url).read() ,encoding='utf8') #lines()
    data = [day[:-2].split(',') for day in days]
    return data
def getUsernamePassword(file):
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

#use ansi color codes to color fg and bg : http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html; curses is an alternative
def ColorCode10pt2f(number):
    if number>0: 
        print(("\033[32m %10.2f"% (number)), end=' ') #suppress newline
    else:
        print(("\033[31m %10.2f"% (number)), end=' ') 

def ColorCode10pt2fRelative(number,comparedto):
    if number>comparedto: 
        print(("\033[32m %10.2f"% (number)), end=' ') #suppress newline
    else:
        print(("\033[31m %10.2f"% (number)), end=' ') 

def ColorCode8s(string):
        print(("\033[31m %8s"% (string)))

def txtReport(Host,User,Password,From,To,Subject,Message):
    try:
        server=smtplib.SMTP(Host)
        server.login(User,Password)
        server.sendmail(From,[To],Message)
        server.quit()
    except smtp.SMTPException:
        print("Error sending text message")

def PrintHeader():
    print(("%7s %10s %10s %10s %10s %10s %10s %10s %10s %10s %6s"  % ("ticker","$ gain", "ann %","% gain","Curr Worth", "Today chg$","Curr Price", "Prev Close" , "52 High","52 Low", "Trend") ))


def PrintHeader2():
    print(("%s %s %12s %12s %12s %12s %12s %12s %2s %12s %6s %12s %12s %12s %5s"  % ("ticker","$ gain", "ann %","% gain","Curr Worth", "Today chg $","Curr Price", "Prev Close" , "52 High","52 Low", "Trend", "Sale Tk Home","Sale Taxes","Disc4Taxes", "HiLoPct") ))

def PrintBanner(input):
    print("#######################################################################")
    print('                          ',input)
    print("#######################################################################")

class Accumulator:
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
        self.dailypercentchange=((self.dailytotalgains+self.dailytotallosses)/(self.portfolioworth-self.dailytotallosses-self.dailytotalgains)*100)
    def Print(self):
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
'''
class Compare:
take a Stock object and Compare it to a given ComparisonStock

allow a special keyword for a ComparisonStock that will allow a given return i.e. 10% annual return.
'''

def padDate(MMDDYYYYDate):
    if len(MMDDYYYYDate)!=10:
        temp=MMDDYYYYDate.split('/')
        purchasedate=datetime.date(int(temp[2]),int(temp[0]),int(temp[1]))
        paddedDate=strftime("%m%d%Y")
    else:
        paddedDate=MMDDYYYYDate
    return paddedDate

def convertToYYYYMMDD(MMDDYYYYDate):# don't need to pad date as the strftime takes care of padding it.
    temp=MMDDYYYYDate.split('/')
    tempdate=datetime.date(int(temp[2]),int(temp[0]),int(temp[1]))
    return tempdate.strftime("%Y%m%d")
    
def get_historical_prices_plus_one_day(symbol, date):
    """
    Get historical prices for the given ticker symbol.
    Returns a nested list.
    date in YYYYMMDD format
    
    """
#the date goes month(jan=0) day year
#http://ichart.yahoo.com/table.csv?s=alxn&d=2012&e=11&f=03&g=d&a=2012&b=10&c=22&ignore=.csv
#http://download.finance.yahoo.com/d/quotes.csv?s=alxn&d=2012&e=11&f=03&g=dtw7&a=2012&b=10&c=22&ignore=.csv aaggh it should be m d y not y m d

#why does the c=... line break? would having date as a Python Date object simply this? then I could use strftime to print out the desired bits.
#it appears my date format from the script I was previously using get_historical_prices... had a diff format. there were separators in it.
    # print(date,symbol)
    # print(int(date[:4]))
    # print(int(date[5:7]),int(date[4:6]))
    # #print(int(date[8:]),int(date[6:]))
    # print(int(date[6:]),int(date[6:]))
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
#        print(day)
        dayStr = str(day, encoding='utf8')
        data.append( dayStr[:-2].split(','))
        #print('his',data) #Need to fix this so that we get the close data that we want.
    return data[1][6] #return the Adj Close value, this takes splits into acct #this is kinda willy nilly since we don't check that we get valid results.


def getSharePrice(ticker):
#the date goes month(jan=0) day year
#test strings
#http://download.finance.yahoo.com/d/quotes.csv?s=alxn&f=l1 # gets only for today
#http://ichart.yahoo.com/table.csv?s=alxn&f=p # gets all available records
#    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1p' #l1-> last trade wo time, p->prev close
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %ticker + '&f=l1' #l1-> last trade wo time, p->prev close
    days = str(urllib.request.urlopen(url).read() , encoding='utf8')  
    data = days[:-2].split(',') 
    #print(data[0])
    return data[0]

#class to allow easy comparison to SP500,Nasdaq performance over same period
#I really need an all purpose method to do comparisons

class MiniStock:
    def __init__(self,data):
        self.ticker=data['ticker']
        #self.purchaseDate=data['purchaseDate']
        temp=data["purchaseDate"].split('/')
        self.purchaseDate=datetime.datetime(int(temp[2]),int(temp[0]),int(temp[1]))

        self.totalPurchasePrice=data['totalPurchasePrice']
        self.commissionToBuy=data['commissionToBuy']
#        self.unitPriceAtPurchase=get_historical_prices_plus_one_day(self.ticker,convertToYYYYMMDD(self.purchaseDate))
        self.unitPriceAtPurchase=get_historical_prices_plus_one_day(self.ticker,(self.purchaseDate.strftime('%Y%m%d')))
        self.unitPriceAtPresent=getSharePrice(self.ticker)

    def GetGainLoss(self):
#        print(self.unitPriceAtPresent,self.unitPriceAtPurchase)
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
        print("%5s %s %s %s %s %s %s %s" % ("buy date","init inv","tickr","gain/loss","tickr","gain/loss","value1","value2" ))
    def printComparison(self):
        self.Header()
#        print(self.miniStock1.GetPurchaseDate(),self.miniStock1.GetTotalPurchasePrice(),self.miniStock1.GetTicker(),self.miniStock1.GetGainLoss(),self.miniStock2.GetTicker(),self.miniStock2.GetGainLoss())

#        print("%s %6.2f %s %2.4f %s %2.4f %6.2f vs %6.2f"% (self.miniStock1.GetPurchaseDate(),self.miniStock1.GetTotalPurchasePrice(),self.miniStock1.GetTicker(),ColorCode10pt2f(self.miniStock1.GetGainLoss(),1),self.miniStock2.GetTicker(),ColorCode10pt2f(self.miniStock2.GetGainLoss(),1),self.miniStock1.GetTotalPurchasePrice()*self.miniStock1.GetGainLoss(),self.miniStock1.GetTotalPurchasePrice()*self.miniStock2.GetGainLoss()))
        print("%5s %6.2f %5s"  % (self.miniStock1.GetPurchaseDate(),self.miniStock1.GetTotalPurchasePrice(),self.miniStock1.GetTicker()),end=' ')
        ColorCode10pt2fRelative(self.miniStock1.GetGainLoss(),1)
        DefaultColorCoding() 
        print(" %5s " % (self.miniStock2.GetTicker()), end=' ')
        ColorCode10pt2fRelative(self.miniStock2.GetGainLoss(),1)
        DefaultColorCoding() 

#        print(" %6.2f vs %6.2f" % ( float(self.miniStock1.GetTotalPurchasePrice()*self.miniStock1.GetGainLoss()),float(self.miniStock1.GetTotalPurchasePrice()*self.miniStock2.GetGainLoss())))

#        ColorCode10pt2f(self.miniStock1.GetTotalPurchasePrice()*self.miniStock1.GetGainLoss(),self.miniStock1.GetTotalPurchasePrice()*self.miniStock2.GetGainLoss())
        self.printBest()

    def printBest(self):
        total1=self.miniStock1.GetTotalPurchasePrice()*self.miniStock1.GetGainLoss()
        total2=self.miniStock1.GetTotalPurchasePrice()*self.miniStock2.GetGainLoss()
        ColorCode10pt2fRelative(total1,total2)
        DefaultColorCoding()
        print( " vs ", end= ' ')
        ColorCode10pt2fRelative(total2,total1)
        DefaultColorCoding()
        print("")

def printCompareHeader():
#    print("%10s %6s %5s %10s %5s %10s %10s %s %10s" % ("buy date","InitInv","tickr","gain/loss","tickr","gain/loss","value1"," vs ","value2" ))
    print("  buy date  InitInv  tickr  gain/loss     tickr      gain/loss       value1            value2" )
# 2003-10-23 1879.12 %5EIXIC        1.62     %5EGSPC         1.39        3049.41     vs      2613.14

# ==================---------- SPDRs ----------==================
#   buy date InitInv tickr  gain/loss tickr  gain/loss     value1  vs      value2
# 2012-10-01  36.93   xlb        0.99       xle         0.98          36.53     vs        36.30


class CompareStock:
    def __init__(self,stockdata1,stockdata2):
#create two ministock objects  
#is there a better way to utilize objects? init the object and pass it in and copy or deepcopy it? Hmm that doesn't seem right bc then there is the original hanging out there that is just taking up space.
        self.Stock1=stockdata1
        self.Stock2=stockdata2

    def printComparison(self):
        print("%5s %6.2f %5s"  % (self.Stock1.GetPurchaseDateYYYY_MM_DDFormatted(),self.Stock1.GetTotalPurchasePrice(),self.Stock1.GetTicker()),end=' ')
        ColorCode10pt2fRelative(self.Stock1.GetGainLoss(),1)
        DefaultColorCoding() 
        print(" %5s " % (self.Stock2.GetTicker()), end=' ')
        ColorCode10pt2fRelative(self.Stock2.GetGainLoss(),1)
        DefaultColorCoding() 
        self.printBest()

    def printBest(self):
        total1=self.Stock1.GetTotalPurchasePrice()*self.Stock1.GetGainLoss()
        total2=self.Stock1.GetTotalPurchasePrice()*self.Stock2.GetGainLoss()
        ColorCode10pt2fRelative(total1,total2)
        DefaultColorCoding()
        print( " vs ", end= ' ')
        ColorCode10pt2fRelative(total2,total1)
        DefaultColorCoding()
        print("")
        
    
class Stock:
        currentshareprice=0.0
        percentgainloss=0.0
        pricegainloss=0.0
        annualizedgainloss=0.0
        shareopenprice=0.0
        shareprevcloseprice=0.0
        taxbracket=0 
        filingstatus=""
        def __init__(self, data): #ticker,sharequantity,totalpurchaseprice,purchasedateyear,purchasedatemonth,purchasedateday,commission_to_buy,commission_to_sell):
            self.ticker=data["ticker"]
            self.sharequantity=float(data["shares"]) #allow for partial shares, useful for mutual funds, and reverse splits
            self.totalpurchaseprice=float(data["totalPurchasePrice"])

            #only purchasedate used
            temp=data["purchaseDate"].split('/')
            self.purchasedate=datetime.datetime(int(temp[2]),int(temp[0]),int(temp[1]))
            # self.purchasedateyear=temp[2]
            # self.purchasedatemonth=temp[0]
            # self.purchasedateday=temp[1]

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

        def getDictionary(self):
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
#            output['']=self.
#            output['']=self.
#            output['']=self.

            return output
            
        def getTaxBracket_func(self):
            input=open(os.path.expanduser("~/Git/PythonStockTracker/TaxBracket.txt"))
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
#            print(self.percentgainloss)<-- this never gets set. I
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
            return (((self.dollarGain/self.totalpurchaseprice+1)**(1/self.yearsSincePurchase()) -1 ) *100)

        def stockSaleTaxes_func(self): #calculate amount you would pay in taxes on your stock sale, taxed only on gains!
            if self.currentWorth_func()>self.totalpurchaseprice-self.commission_to_buy:
                output=(self.currentWorth_func()-self.totalpurchaseprice+self.commission_to_buy)*self.taxRate_func()
            else:
                output=0 #we're in the red. Not sure just yet how the taxes apply here
            return output

        def stockSaleTakeHome_func(self): #calculate amount you would receive after taxes on your stock sale
            if self.currentWorth_func()>self.totalpurchaseprice-self.commission_to_buy:
                output=self.currentWorth_func()-(self.currentWorth_func()-self.totalpurchaseprice+self.commission_to_buy)*self.taxRate_func() 
            else:
                output=0 #we're in the red. Not sure just yet how the taxes apply here
            return output

        def stockpriceDiscountedForTaxes_func(self): #the effective price the stock would appear when selling, taking into acct deductions for taxes: e.g. a $120 stock bought for $20 at a 38% tax rate would appear as a $82 stock -> 120-(120-20)*.38
            return self.currentshareprice*self.oneMinusTaxRate_func()
        def oneMinusTaxRate_func(self): #add column to input file for personal info that includes tax rate, LT ST capital gains, This function will need to be update proly every year to take in tax changes
            if self.yearsSincePurchase()>1:
                taxrate=(100-self.calculateLongTermCapitalGains_func())/100  #<-- due to pythons untyped variables this is evaluated as an int even when wrapped in float()
                taxrate=(100-self.calculateLongTermCapitalGains_func())/100.0 #<-- turning the denominator in a float types the whole thing as a float
            else:
                taxrate=(100-self.calculateShortTermCapitalGains_func())/100.0
            return taxrate
            #return float((100-self.calculateLongTermCapitalGains_func())/100.0)
        def taxRate_func(self): #add column to input file for personal info that includes tax rate, LT ST capital gains, This function will need to be update proly every year to take in tax changes
            if self.yearsSincePurchase()>1:
                taxrate=(self.calculateLongTermCapitalGains_func())/100.0
            else:
                taxrate=(self.calculateShortTermCapitalGains_func())/100.0
            return taxrate
        def calculateLongTermCapitalGains_func(self):
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
            if self.share52wkhigh!=0 and self.share52wklow!=0:
                return (self.currentshareprice-self.share52wklow)/(self.share52wkhigh-self.share52wklow)
            else:
                return 0
            
    
        def PrintCompact2(self):
            print((" %8s %8.2f %8.2f %8.2f %8.2f %8.2f %8.2f"  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice,self.sharequantity*(self.currentshareprice - self.shareprevcloseprice),self.currentshareprice,self.shareprevcloseprice)))
            
        def PrintForTxtMessage(self):
            message="Ticker: %8s $+-: %8.2f AnnlRet: %8.2f Worth:%8.2f DayChange:%8.2f"  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice,self.sharequantity*(self.currentshareprice - self.shareprevcloseprice  ))
            return  message
        def PrintCompact(self):
            print((" %8s %8.2f %8.2f %8.2f "  % (self.ticker,self.dollarGain,self.annualizedReturn,self.currentWorth_func())))
                
        def PrintColorized(self):
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
            print(("%2.5f" %( self.yearsSincePurchase() )))
#NOTE:
#I could make these print functions more multipurpose by defining a function that outputs a new line and otherwise you prevent the newline from being added. Then just pick and choose which statements you want printed.
                
        def getSharePrice(self):
# data format found in GetStockQutoesv2.sh
#the date goes month(jan=0) day year

#we actually need to get the prev close to compute gain for the day. Wall Street doesn't compute the gain from the open, but from prev close
            url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1opwt7'

            days = str(urllib.request.urlopen(url).read() , encoding='utf8')  #lines()
            data = days[:-2].split(',') 
            if float(data[0])==0.0:
                print("Uhh bad stock ticker")
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

        def resultsIfInvestedInSP500(self):
            avgAnnualReturn=1.10 #10% annual return
#            print(self.yearsSincePurchase(),self.totalpurchaseprice,avgAnnualReturn)
            return (self.totalpurchaseprice*(avgAnnualReturn**self.yearsSincePurchase())) #I'm not sure if this is completely accurate due to partial years etc. and avg daily rates possibly being diff. need to research this.

        def yearsSincePurchase(self):#is there an easier way to do this with the built in time functions?-->doesn't appear to be : http://www.python-forum.org/pythonforum/viewtopic.php?f=3&t=4553  http://stackoverflow.com/questions/4436957/pythonic-difference-between-two-dates-in-years http://stackoverflow.com/questions/6451655/python-how-to-convert-datetime-dates-to-decimal-years http://www.google.com/search?q=fraction+years+between+dates+python&oq=fraction+years+between+dates+python&sugexp=chrome,mod=0&sourceid=chrome&ie=UTF-8
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
            

#this methoad traverses a portfolio and outputs the performance of each stock in the portfolio
#as well as overall performance.
def StockTable(inputfilename):
#Uncomment me to get the original StockTrackerJSON functionality back.
    input=open(inputfilename)
    outputlist=[]
    data_string=json.load(input)
    emailReportMsg=""
    for portfolio in data_string["portfolio"]:
        if portfolio["display"] == "yes":
            print('==================----------',portfolio["portfolioName"],'----------==================')

            DefaultColorCoding()
            PrintHeader2()

            cumulative=Accumulator()
            emailReportMsg+=portfolio["portfolioName"]
            for data in portfolio["portfolioStocks"]:
                #print(data)
                
                stock=Stock(data)
                cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain,stock.dailyChange_func() ,stock.currentWorth_func() )
                stock.PrintColorized3() #includes theoretical "what if" invested in SP500 instead
                #            stock.PrintColorized2()
                message=stock.PrintForTxtMessage()
                #outputlist.append(stock.getDictionary())
                emailReportMsg+="stock data" #stock+','
            emailReportMsg+=cumulative.JSONify()+",\n"
            cumulative.Print()
            DefaultColorCoding()
    input.close()
    emailReport("smtp.gmail.com",587,"username","password","N a K","5079909052@tmomail.net","Daily Mkt Report",emailReportMsg)

    print(emailReportMsg)
    return stock.getDictionary() #outputlist #emailReportMsg
#    print(message)

def MongoStockTable(inputfilename):
#Uncomment me to get the original StockTrackerJSON functionality back.
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


def MongoSave(message):
    client = pymongo.MongoClient("localhost",27017)
    db = client.PortfolioTracker
    db.AllPortfolios.save(message)#this must be a dictionary for proper insertion http://docs.python.org/2/tutorial/datastructures.html#dictionaries
#http://docs.mongodb.org/manual/tutorial/getting-started-with-the-mongo-shell/

def Alert(inputfilename,alertPercent):
#Uncomment me to get the original StockTrackerJSON functionality back.
    
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


#this method takes traverses a portfolio and compares the performance of the two stocks against each other.
#the first stock's purchase date is used to perform the benchmark.
#the performance of each stock from that purchase date is calculated
#the print out shows each stock's return from the purchase data as welll as what that initial investment is and what it 
#would've turned into if the second stock was purchased instead.
def ComparePortfolio(inputfilename):
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
    print("python StockTrackerJSON  [ -c/--comparison, -i/--input=portfolio.json -s/--stocktable ]")
    print("python StockTrackerJSON -iPortfolio.json -c -s")

############ Main 

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
print(sys.argv[1:])
#pretty much straight from : http://docs.python.org/release/3.1.5/library/getopt.html
#took me a while to catch that for py3k that you don't need the leading -- for the long options
#sadly optional options aren't allowed. says it in the docs :( http://docs.python.org/3.3/library/getopt.html
try:
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'a:e:csi:m', ['alert=',
                                                                   'compare',
                                                                   'stocktable',
                                                                   'input=',
                                                                      'email=',
                                                                       'mongo'
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

PrintBanner(inputfilename)
if stocktableflag:
    StockTable(inputfilename)
if comparisonflag:
    ComparePortfolio(inputfilename)
if alertflag:
    Alert(inputfilename,alertPercent)
if mongoflag:
    MongoStockTable(inputfilename)
#    MongoSave(StockTable(inputfilename))#.JSONify())
#    MongoSave("{ 'name':'bob', 'hair':'bald'}")#.JSONify())
print("") #otherwise 


"""
emailReport("smtp.djinnius.com","587","deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly")
emailReport("smtp.djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly2")
emailReport("djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly3")
#emailReport("mail.djinnius.com",587,"dals","backctry","NAK","5079909052@tmomail.net","stuff","hello McFly")
# this guy works: emailReport("smtp.gmail.com",587,"nick.klosterman@gmail.com","XXXXXXXXXX","NAK","5079909052@tmomail.net","testnick","test subjetct")

"""
