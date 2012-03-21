#!/usr/bin/python
import datetime
import urllib
import smtplib #for emailing reports
#now=datetime.datetime.now()
#'nick':datetime.datetime(1978,7,2)
#days_ago=(now-when).days

#class StockList:
#    def __init__(self,

def isLeapYear(year):
    leapyear=0
    if year%4==0:
        leapyer=1
    return leapyear

def getSharePrices(tickerlist):
#tickerlist should be a set of ticker symbols with '+' in between
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %tickerlist + '&f=l1'
#            url = 'http://download.finance.yahoo.com/d/quotes.csv?s=AAPL&f=l1' l1=>last trade without time.
    days = urllib.urlopen(url).read() #lines()
    data = [day[:-2].split(',') for day in days]
    return data
def emailReport(Host,Port,User,Password,From,To,Subject,Message):
    try:
        server=smtplib.SMTP(Host,Port)
        server.login(User,Password)
        server.sendmail(From,[To],Message)
        server.quit()
        print("Successfully sent email")
    except SMTPException:
        print("Error: unable to send email")

def txtReport(Host,User,Password,From,To,Subject,Message):
    server=smtplib.SMTP(Host)
    server.login(User,Password)
    server.sendmail(From,[To],Message)
    server.quit()
    
class Stock:
        currentshareprice=0.0
        percentgainloss=0.0
        pricegainloss=0.0
        annualizedgainloss=0.0
        shareopenprice=0.0
        shareprevcloseprice=0.0

        def __init__(self, data): #ticker,sharequantity,totalpurchaseprice,purchasedateyear,purchasedatemonth,purchasedateday,commission):
            self.ticker=data[0]
            self.sharequantity=int(data[1])
            self.totalpurchaseprice=float(data[2])
            temp=data[3].split('/')
#            print temp
            self.purchasedate=datetime.datetime(int(temp[2]),int(temp[0]),int(temp[1]))
            self.purchasedateyear=temp[2]
            self.puchasedatemonth=temp[0]
            self.purchasedateday=temp[1]
            self.commission=data[4]
#            self.currentshareprice=self.getSharePrice()
            self.getSharePrice()
            self.dollarGain=self.dollarGain_func()
            self.percentGain=self.percentGain_func()
            self.annualizedReturn=self.annualizedReturn_func()

        def percentGain_func(self): 
            return (self.sharequantity*self.currentshareprice-self.totalpurchaseprice)/self.totalpurchaseprice
        def dollarGain_func(self):
            return float(self.sharequantity*self.currentshareprice-self.totalpurchaseprice)
        def annualizedReturn_func(self):
            return (((self.dollarGain/self.totalpurchaseprice+1)**(1/self.yearsSincePurchase()) -1 ) *100)
        def PrintData(self):
            print("-----------------=======================-----------------")
            print("Ticker:"+self.ticker)
            print("Shares:"+str(self.sharequantity))
            print("Total Purchase Price:"+str(self.totalpurchaseprice))
            print("Purchase Date:"+str(self.purchasedate))
            print("Dollar Gain:"+str(self.dollarGain))
            print("Percent Gain:"+str(self.percentGain))
            print("Annualized Return:"+str(self.annualizedReturn))
            print("Current Value:"+str(self.sharequantity*self.currentshareprice))
            print("Current Share Price:"+str(self.currentshareprice))
            print("Current Open  Price:"+str(self.shareopenprice))
        def PrintCompact2(self):
            print(" %8s %8.2f %8.2f %8.2f %8.2f"  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice,self.sharequantity*(self.currentshareprice - self.shareprevcloseprice  )))
        def PrintForTxtMessage(self):
            message="Ticker: %8s $+-: %8.2f AnnlRet: %8.2f Worth:%8.2f DayChange:%8.2f"  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice,self.sharequantity*(self.currentshareprice - self.shareprevcloseprice  ))
            return  message
        def PrintCompact(self):
#            print("-----------------=======================-----------------"
#            print self.ticker+"\t"+str(self.dollarGain)+"\t"+str(self.annualizedReturn)+"\t"+str(self.sharequantity*self.currentshareprice)
            print(" %8s %8.2f %8.2f %8.2f "  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice ))
                
        def getSharePrice(self):
# data format found in GetStockQutoesv2.sh
#the date goes month(jan=0) day year
            url = 'http://ichart.yahoo.com/table.csv?s=%s&' % self.ticker + \
                'f=l1' #&ignore.csv'
#we actually need to get the prev close to compute gain for the day. we don't compute the gain from the open
            url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1op'

            days = urllib.urlopen(url).read() #lines()
            data = days[:-2].split(',') 
            if float(data[0])==0.0:
                print("Uhh bad stock ticker")
            self.currentshareprice=float(data[0])
            self.shareopenprice=float(data[1])
            self.shareprevcloseprice=float(data[2])

        def yearsSincePurchase(self):
            now=datetime.datetime.now()
            daysElapsed=(now-self.purchasedate).days
            #if self.purchase
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
#            print daysDiff
#            print float(days2/daysinyear)
#            print yearsElapsed+daysDiff
            return yearsElapsed+daysDiff
            

#TODO: create Portfolio object and have a total for the entire portfolio
#todo: trend line of +-+-++ for last few days worth of trading,
#generic line for an index. as comparison

"""
stock=Stock("aapl",142,1400,2000,10,2,7)
stock=Stock("fmcc.obb",142,1400,2000,10,2,7)
#stock=Stock("aapl",142,1400,2012,03,2,7)
stock.getSharePrice()
stock.yearsSincePurchase()
pctgain=stock.percentGain_func()
dlrgain=stock.dollarGain_func()
#print pctgain
#print dlrgain
stock.PrintData()


        def __init__(self, ticker,sharequantity,totalpurchaseprice,purchasedateyear,purchasedatemonth,purchasedateday,commission):
            self.ticker=data[0]
            self.sharequantity=int(sharequantity)
            self.totalpurchaseprice=float(totalpurchaseprice)
            self.purchasedate=datetime.datetime(purchasedateyear,purchasedatemonth,purchasedateday)
            self.purchasedateyear=purchasedateyear
            self.puchasedatemonth=purchasedatemonth
            self.purchasedateday=purchasedateyear
            self.commission=commission
#            self.currentshareprice=self.getSharePrice()
            self.getSharePrice()
            self.dollarGain=self.dollarGain_func()
            self.percentGain=self.percentGain_func()
            self.annualizedReturn=self.annualizedReturn_func()

"""

#def Portfolio:

"""
input=open("StockData.txt")
#    print(" %8s %8.2f %8.2f %8.2f "  % ("ticker"," $ gain", "ann %","Curr Worth")
#print(" %8s %8s %8s %8s "  % ("ticker"," $ gain", "ann %","Curr Worth")
print(" %8s %8s %8s %8s %11s"  % ("ticker"," $ gain", "ann %","Curr Worth", "Today $ chg" )
for line in input:
    data=""
    if line.strip(): #skip blank lines
        if line[0]!='#': #skip comments
            data=line[:-1].split(',')
            stock=Stock(data)
            #print data[0],data[3]
#           stock.PrintData()
            stock.PrintCompact2()
            message=stock.PrintForTxtMessage()
            print(message)
            emailReport("mail.djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff",stock.PrintForTxtMessage())
#    print data
"""
emailReport("mail.djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly")
emailReport("mail.djinnius.com",587,"deals","backcountry","NAK","nickklosterman@gmail.com","stuff","hello McFly")
#emailReport("mail.djinnius.com",587,"dals","backctry","NAK","5079909052@tmomail.net","stuff","hello McFly")
