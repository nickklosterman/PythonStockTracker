#!/usr/bin/python

import datetime
import urllib.request, urllib.parse, urllib.error
import smtplib #for emailing reports
import os #for converting ~ -> users home directory
import json

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
def emailReport(Host,Port,User,Password,From,To,Subject,Message):
    try:
        server=smtplib.SMTP()
        server.connect(Host,Port)
        server.starttls()
#        server.set_debuglevel(1)   
        server.login(User,Password)
        server.sendmail(From,[To],Message)
        server.quit()
        print("Successfully sent email")
    except smtp.SMTPException:
        print("Error: unable to send email")

#use ansi color codes to color fg and bg : http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html; curses is an alternative
def ColorCode10pt2f(number):
    if number>0: 
        print(("\033[32m %10.2f"% (number)), end=' ') #suppress newline
    else:
        print(("\033[31m %10.2f"% (number)), end=' ') 
def ColorCode8s(string):
        print(("\033[31m %8s"% (string)))

def txtReport(Host,User,Password,From,To,Subject,Message):
    server=smtplib.SMTP(Host)
    server.login(User,Password)
    server.sendmail(From,[To],Message)
    server.quit()

def PrintHeader():
    print(("%7s %10s %10s %10s %10s %10s %10s %10s %10s %10s %6s"  % ("ticker","$ gain", "ann %","% gain","Curr Worth", "Today chg$","Curr Price", "Prev Close" , "52 High","52 Low", "Trend") ))


def PrintHeader2():
    print(("%s %s %12s %12s %12s %12s %12s %12s %2s %12s %6s %12s %12s %12s %5s"  % ("ticker","$ gain", "ann %","% gain","Curr Worth", "Today chg $","Curr Price", "Prev Close" , "52 High","52 Low", "Trend", "Sale Tk Home","Sale Taxes","Disc4Taxes", "HiLoPct") ))


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
            temp=data["purchaseDate"].split('/')
            self.purchasedate=datetime.datetime(int(temp[2]),int(temp[0]),int(temp[1]))
            self.purchasedateyear=temp[2]
            self.puchasedatemonth=temp[0]
            self.purchasedateday=temp[1]
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
            
        def getTaxBracket_func(self):
            input=open(os.path.expanduser("~/Git/PythonStockTracker/TaxBracket.txt"))
            for line in input:
                data=""
                if line.strip(): #skip blank lines
                    if line[0]!='#': #skip comments
                        data=line[:-1].split(',')
                        self.taxbracket=int(data[0])
                        self.filingstatus=data[1]


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


        def yearsSincePurchase(self):
            now=datetime.datetime.now()
            daysElapsed=(now-self.purchasedate).days
            yearsElapsed=now.year-self.purchasedate.year
            daysCalc=datetime.datetime(now.year,self.purchasedate.month,self.purchasedate.day)
            days2=(now-daysCalc).days
            if days2 <0: #the case when trying to do june 6-Oct 8, so have to subtract a year 
                yearsElapsed=yearsElapsed-1
                daysCalc=datetime.datetime(now.year-1,self.purchasedate.month,self.purchasedate.day)
                days2=(now-daysCalc).days
                
            daysinyear=365.0 #force to be float so the division works as we would expect
            yr=now.year
            if isLeapYear(yr): #now.year):
               daysinyear+=1
            daysDiff=(days2/daysinyear)
            return yearsElapsed+daysDiff
            

#TODO: create Portfolio object and have a total for the entire portfolio
#todo: trend line of +-+-++ for last few days worth of trading,
#generic line for an index. as comparison


############ Main 

#use ncurses, ansi color codes

from  textwrap import TextWrapper
wrapper =TextWrapper()
wrapper.width=190 #set text wrapping width manually otherwise if drag terminal to full width python doesn't write text out the full width

import sys
if len(sys.argv)>1:
    if sys.argv[1]!="":
        inputfilename=sys.argv[1]
else:
    inputfilename="AllPortfolios.json"

import os.path
#loop over command line args
sysargvlength=len(sys.argv)
#0th element is the script name
i=1
while i <= sysargvlength:
    if sysargvlength>1 and os.path.isfile(sys.argv[i]):
        inputfilename=sys.argv[i]
    i+=1

    input=open(inputfilename)
    data_string=json.load(input)
    for portfolio in data_string["portfolio"]:
        print('==================----------',portfolio["portfolioName"],'----------==================')

        DefaultColorCoding()
        PrintHeader2() #2()

        cumulative=Accumulator()

        for data in portfolio["portfolioStocks"]:
            #print(data)
            stock=Stock(data)
            cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain,stock.dailyChange_func() ,stock.currentWorth_func() )
            stock.PrintColorized2()
            message=stock.PrintForTxtMessage()

        cumulative.Print()
        DefaultColorCoding()
    input.close()
    print("")


"""
emailReport("smtp.djinnius.com","587","deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly")
emailReport("smtp.djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly2")
emailReport("djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly3")
#emailReport("mail.djinnius.com",587,"dals","backctry","NAK","5079909052@tmomail.net","stuff","hello McFly")
# this guy works: emailReport("smtp.gmail.com",587,"nick.klosterman@gmail.com","p51mustang","NAK","5079909052@tmomail.net","testnick","test subjetct")

"""
