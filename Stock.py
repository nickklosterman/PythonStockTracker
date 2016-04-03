import datetime
import os #for converting ~ -> users home directory
import urllib.request, urllib.parse, urllib.error
import json

import HTMLColorCode as HCC
import TerminalColorCoding as TCC
import DateTimeHelpers as DTH
import StockHelper


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
    share52wkhigh=0.1
    share52wklow=0.001
    trend=""
    taxbracket=0 
    filingstatus=""
    def __init__(self, data,shareprice): #ticker,sharequantity,totalpurchaseprice,purchasedateyear,purchasedatemonth,purchasedateday,commission_to_buy,commission_to_sell,):
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
            
        self.taxBracketFile=data["taxBracketFile"]

        if (shareprice=="0.01%" or shareprice=='N/A'):  # prrxx returns 0.01% as price. assign value of $1/share
            shareprice=1.0
        self.getSharePrice() #needed so that prev and trends are populated.
        
        try:
            self.currentshareprice = float(shareprice)
        except ValueError:
            self.currentshareprice = 0
        

        if self.currentshareprice ==0.0 :
            self.getSharePrice()

        if False:
            if float(shareprice)<0:
                self.currentshareprice = float(shareprice)


  

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

        #output="<tr><td> {0} {1} {2} {1} {3} {1} {4} {1} {5:,.2f} {1} {6} {1} {7:,.2f} {1} {8:,.2f} {1} {9:,.2f} {1} {10:,.2f} {1} {11} {1} {12:,.2f} {1} {13:,.2f} {1} {14:,.2f} {1} {15:,.2f} {1} {16:} {1} {17:,.2f}</td></tr>".format(
        output='<tr><td> {0} {1} {2} {1} {3} {1} {4} {1} {5:,.2f} {1} {6} {1} {7:,.2f} {1} {8:,.2f} {1} {9:,.2f} {1} {10:,.2f} {1} <img src="http://ichart.finance.yahoo.com/z?s={11}&t=1y&q=l&l=on&z=s&p=m100,&a=&c=%5EGSPC&lang=en-US&region=US"> {1} {12:,.2f} {1} {13:,.2f} {1} {14:,.2f} {1} {15} {1} {16:} {1} {17:,.2f}</td></tr>'.format(
self.tickerLink(), 
separator, 
HCC.htmlTableColorCode(self.dollarGain), 
HCC.htmlTableColorCode(self.annualizedReturn), 
HCC.htmlTableColorCode(self.percentGain_func()), 
self.currentWorth_func(), 
HCC.htmlTableColorCode(self.dailyChange_func()), 
self.currentshareprice, 
self.shareprevcloseprice, 
self.share52wkhigh, 
self.share52wklow, 
self.ticker,             #self.trend,
self.stockSaleTakeHome_func(), 
self.stockSaleTaxes_func(), 
self.stockpriceDiscountedForTaxes_func(), 
HCC.htmlTableColorCodeDecimal(self.FiftyTwoWeekHighLowFactor()),
HCC.htmlTableComparisonColorCode(self.resultsAlphaVsSP500(), 0 ),
self.yearsSincePurchase() )
    
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
        output['TimeStamp']=datetime.datetime.now()
        return output
            
    def getTaxBracket_func(self):
        """
        Read in the tax bracket and filing status from the given file 
        these fields are then used for 
        """
        input=open(os.path.expanduser(self.taxBracketFile)) #the os.path.expanduser is unnecessary unless you are using the ~ to denote the user's home path
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
        if (self.totalpurchaseprice != 0):
            return (self.sharequantity*self.currentshareprice-self.totalpurchaseprice)/self.totalpurchaseprice
        else:
            return 0.0
    def percentGainLoss_func(self): #not sure what a good term for this is ROI?
        if (self.totalpurchaseprice != 0):
            return (self.sharequantity*self.currentshareprice)/self.totalpurchaseprice
        else:
            return 0.0

    def dollarGain_func(self):
        return float(self.sharequantity*self.currentshareprice-self.totalpurchaseprice)

    def annualizedReturn_func(self):
        """
        Calculate the annualized rate of return for this investment
        """
        ARR=0
        #I was encountering an overflow issue when the cash/prrxx was calculated
        if (self.yearsSincePurchase() > 0 and self.totalpurchaseprice !=0 and self.ticker != 'prrxx'):
            ARR=(((self.dollarGain/self.totalpurchaseprice+1)**(1/self.yearsSincePurchase()) -1 ) *100)
        return ARR 

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

        discountedPrice = 0
        if self.sharequantity > 0:
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
            if self.share52wklow==-1 and self.share52wkhigh==-1:
                return 0
            else:
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
        print(("%10.2f" % (self.currentWorth_func())), end=' ') 
        ColorCode10pt2f(self.dailyChange_func()) 
        print(("%10.2f %10.2f" %(self.currentshareprice,self.shareprevcloseprice)), end=' ')
        print(("\033[49m \033[39m"), end=' ') #reset color to default
        print(("%10.2f %10.2f %6s" %(self.share52wkhigh,self.share52wklow,self.trend)))

    def PrintColorized2(self):
        """
        Not Used
        """
        print(("%7s"  % (self.ticker)), end=' ')
        TCC.ColorCode10pt2f(self.dollarGain)
        TCC.ColorCode10pt2f(self.annualizedReturn)
        TCC.ColorCode10pt2f(self.percentGain_func())
        print(("\033[49m \033[39m"), end=' ')
        print(("%10.2f" % (self.currentWorth_func())), end=' ') 
        TCC.ColorCode10pt2f(self.dailyChange_func()) 
        print(("%10.2f %10.2f" %(self.currentshareprice,self.shareprevcloseprice)), end=' ')
        print(("\033[49m \033[39m"), end=' ') #reset color to default
        print(("%10.2f %10.2f %6s" %(self.share52wkhigh,self.share52wklow,self.trend)), end=' ')
        print(("%10.2f %10.2f %10.2f %10.2f" %(self.stockSaleTakeHome_func(),self.stockSaleTaxes_func(),self.stockpriceDiscountedForTaxes_func(),self.FiftyTwoWeekHighLowFactor())))

    def PrintColorized3(self):
        """
        Print out dollar gain, annualized rate of return, percent gain/loss, current investment worth, daily change of investment, current share price, prev close of share price, 52 wk high, 52 wk low, trend, proceeds you would see if sold immediately, taxes due on such an immediate sale, adjusted stock price taking into account taxes , 52 week high low factor, theoretical results if invested in the SP500, years since purchased
        """
        print(("%7s"  % (self.ticker)), end=' ')
        TCC.ColorCode10pt2f(self.dollarGain)
        TCC.ColorCode10pt2f(self.annualizedReturn)
        TCC.ColorCode10pt2f(self.percentGain_func())
        print(("\033[49m \033[39m"), end=' ')
        print(("%10.2f" % (self.currentWorth_func())), end=' ') 
        TCC.ColorCode10pt2f(self.dailyChange_func()) 
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

        if (self.ticker=="prrxx"):
            self.shareopenprice=1.0
            self.currentshareprice=1.0
            self.shareprevcloseprice=1.0
            self.share52wklow=1.000001
            self.share52wkhigh=1.0
            self.trend="===="
            """        
        elif (databaseflag):
            # I think this will have problmes bc it neeeds to set the other fields as wwell
            self.currentshareprice=getSharePriceFromDatabase(self.ticker)
            """
        elif (self.currentshareprice != 0.0 ):
            self.shareopenprice=1.0 #this then throws off the daily gains 
            self.shareprevcloseprice=1.0
            self.share52wklow=1.000001
            self.share52wkhigh=1.0
            self.trend="===="

        else:
            url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1opwt7'
            print(url)
            #while True:
            for x in range(10):
                try:
                    print(x)
                    data=""
                    #http://stackoverflow.com/questions/802134/changing-user-agent-on-urllib2-urlopen
                    #http://docs.python.org/3.3/library/urllib.request.html#module-urllib.request
                    headers= {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11' }
                    myReq=urllib.request.build_opener()
                    myReq.addheaders = [('User-Agent','Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')] # Request(url,data=b'None',headers)
                    myReq.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')]
                    days=str(myReq.open(url).read() , encoding='utf8')
                    data = days[:-2].split(',') 
                except urllib.error.HTTPError as err:
                    print(err,self.ticker)
                    continue
                except SocketError as e:
                    pass
                    print(e,self.ticker)
                    continue
                except:
                    print('something else broke')
                    continue
                break
            try:
                tempSharePrice=float(data[0])
            except ValueError:
                tempSharePrice=0.0
                
            if tempSharePrice==0.0:
                print("Uhh bad stock ticker: %7s" % self.ticker)
                
            self.currentshareprice=tempSharePrice

            if data[1]!="N/A": #not sure I even need the share open price. I don't do anything with it.
                self.shareopenprice=float(data[1])
            print(data[2])
            if data[2]!="N/A": 
                self.shareprevcloseprice=float(data[2])

            print(data[3])
            if data[3]!="\"N/A - N/A\"" and data[3]!="N/A":
                print(data[3])
                temp=data[3].split(" - ")
                self.share52wklow=float(temp[0][1:])
                self.share52wkhigh=float(temp[1][:-1])
                self.trend=data[4][7:13]
            else:
                self.share52wklow=-1#"-"#0.0001
                self.share52wkhigh=-1#"-"#=0.0002
                self.trend="N/A"





                """
                create a global dict of dates:prices for SP500
                check the list to see if that date's price has all ready been retrieved.
                if not retrieve the price for that day and add it to the list
                
                compute the ARR for the time period X until today
                """

    def resultsIfInvestedInSP500(self):
        print("This needs to be redone such that a dict is created for the purchase dates and SP500 on that day")
        currentSP500=-1
        startSP500=-1
        currentSP500=float(StockHelper.getSharePrice("%5EGSPC"))

        #we need to check if this is the first day for this security, as we can't get historical data if this is the first day
        from datetime import date
        today = date.today()
        if ( self.purchasedate.day == today.day  and self.purchasedate.month == today.month and self.purchasedate.year == today.year):
            startSP500=float(StockHelper.getShareOpenPrice("^GSPC"))
        else:
            startSP500=float(StockHelper.get_historical_price("^GSPC",(self.purchasedate.strftime('%Y%m%d'))))
        if (startSP500 != 0):

            return (self.totalpurchaseprice*(1+(currentSP500-startSP500)/startSP500))
        else:
            return 0

    def resultsIfInvestedInX(self):
        print("This needs to be redone such that a dict is created for the purchase dates and TickerX on that day")
        currentTickerX=-1
        startTickerX=-1
        currentTickerX=float(StockHelper.getSharePrice(self.comparisonticker))

        #we need to check if this is the first day for this security, as we can't get historical data if this is the first day
        from datetime import date
        today = date.today()
        if ( self.purchasedate.day == today.day  and self.purchasedate.month == today.month and self.purchasedate.year == today.year):
            startTickerX=float(StockHelper.getShareOpenPrice(self.comparisonticker))
        else:
            startTickerX =float(StockHelper.get_historical_price(self.comparisonticker,(self.purchasedate.strftime('%Y%m%d'))))
        if (startTickerX != 0):

            return (self.totalpurchaseprice*(1+(currentTickerX-startTickerX)/startTickerX))
        else:
            return 0
        
    def resultsAlphaVsSP500(self):
        print("This needs to be redone such that a dict is created for the purchase dates and SP500 on that day")
        currentSP500=-1
        startSP500=-1
        currentSP500=float(StockHelper.getSharePrice("%5EGSPC"))

        from datetime import date
        today = date.today()
        if ( self.purchasedate.day == today.day  and self.purchasedate.month == today.month and self.purchasedate.year == today.year):
            gspcOpenPrice=StockHelper.getShareOpenPrice("^GSPC")
            if (gspcOpenPrice[0] != "N"): #check for na value, WEAK TEST could do a regex to see if the price contains a letter
                startSP500=float(gspcOpenPrice)
            else:
                startSP500=0.1
        else:
            startSP500 =float(StockHelper.get_historical_price("^GSPC",(self.purchasedate.strftime('%Y%m%d')))) #"%EGSPC",(self.purchasedate.strftime('%Y%m%d')))
        if (startSP500 != 0 and self.totalpurchaseprice != 0 and self.currentWorth_func() !=0):
            return (self.currentWorth_func()-(self.totalpurchaseprice*(1+(currentSP500-startSP500)/startSP500)) ) / ( self.currentWorth_func() )*100  # this returns the percentage over/under (alpha) of the current investment when compared to the SP500 index.; negative values are bad, positive are good
        else:
            return 0
        
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
        if DTH.isLeapYear(yr): #now.year):
            daysinyear+=1
        daysDiff=(days2/daysinyear)
        return yearsElapsed+daysDiff
    def CSV(self):
        """
        Output Stock data as a json object
        """
        separator=","
        data="{0} {1} {2:.2f} {1} {3:.4f} {1} {4:.4f} {1} {5:.2f} {1} {6} {1} {7:.2f} {1} {8:.2f} {1} {9:.2f} {1} {10:.2f} {1} {11} {1} {12:.2f} {1} {13:.2f} {1} {14:.2f} {1} {15} {1} {16:} {1} {17:.2f} {1} {18}".format(
            self.ticker, #0
            separator, #1
            #darn it I need to strip commas from prices for CSV
            self.dollarGain,  #2
            self.annualizedReturn,  #3
            self.percentGain_func(),  #4
            self.currentWorth_func(), #5
            self.dailyChange_func(), #6
            self.currentshareprice, #7
            self.shareprevcloseprice, #8
            self.share52wkhigh, #9
            self.share52wklow, #10
            self.trend, #11
            self.stockSaleTakeHome_func(), #12
            self.stockSaleTaxes_func(), #13
            self.stockpriceDiscountedForTaxes_func(), #14
            self.FiftyTwoWeekHighLowFactor(), #15
            self.resultsAlphaVsSP500(), #16
            self.yearsSincePurchase(), #7
            DTH.GetDateTime() # 18 hmmm I might want a static time such that it isn't diff for each ouptut
        )
         #add in portfolio as last element and get rid of the overarching portfolioname structure. flatten data out this way. can group later via that portfolioname field?; would need to pass in the portfolioname then to accumulator object. 
        return data
        
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


