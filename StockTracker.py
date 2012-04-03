#!/usr/bin/python
import datetime
import urllib
import smtplib #for emailing reports
#now=datetime.datetime.now()
#'nick':datetime.datetime(1978,7,2)
#days_ago=(now-when).days

#class StockList:
#    def __init__(self,
def DefaultColorCoding():
    print("\033[49m \033[39m "), #set to default color coding, suppress newline

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
        print("\033[32m %10.2f"% (number)), #suppress newline
    else:
        print("\033[31m %10.2f"% (number)), 
def ColorCode8s(string):
        print("\033[31m %8s"% (string))

def txtReport(Host,User,Password,From,To,Subject,Message):
    server=smtplib.SMTP(Host)
    server.login(User,Password)
    server.sendmail(From,[To],Message)
    server.quit()

def PrintHeader():
    print("%10s %10s %10s %10s %10s %10s %10s"  % ("ticker"," $ gain", "ann %","Curr Worth", "Today chg$","Curr Price", "Prev Close" ) )
#    print(" %8s %8.2f %8.2f %8.2f "  % ("ticker"," $ gain", "ann %","Curr Worth")
#print(" %8s %8s %8s %8s "  % ("ticker"," $ gain", "ann %","Curr Worth")

class Accumulator:
    def __init__(self):
        self.totalpurchaseprice=0.0
        self.totalcommission=0.0
        self.totaldollargain=0.0
    def Add(self,purchaseprice, commission, dollargain):
        self.totalpurchaseprice+=purchaseprice
        self.totalcommission+=commission
        self.totaldollargain+=dollargain
    def Print(self):
        print("Total Purchase Price: %s" % (self.totalpurchaseprice))
        print("Total Commission Paid: %10.2f" % (self.totalcommission))
        print("Total Dollar Gain/Loss: %10.2f" % (self.totaldollargain))

class Stock:
        currentshareprice=0.0
        percentgainloss=0.0
        pricegainloss=0.0
        annualizedgainloss=0.0
        shareopenprice=0.0
        shareprevcloseprice=0.0

        def __init__(self, data): #ticker,sharequantity,totalpurchaseprice,purchasedateyear,purchasedatemonth,purchasedateday,commission_to_buy,commission_to_sell):
            self.ticker=data[0]
            self.sharequantity=int(data[1])
            self.totalpurchaseprice=float(data[2])
            temp=data[3].split('/')
#            print temp
            self.purchasedate=datetime.datetime(int(temp[2]),int(temp[0]),int(temp[1]))
            self.purchasedateyear=temp[2]
            self.puchasedatemonth=temp[0]
            self.purchasedateday=temp[1]
            self.commission_to_buy=float(data[4])
            self.commission_to_sell=float(data[5])
#            self.currentshareprice=self.getSharePrice()
            self.getSharePrice()
            self.dollarGain=self.dollarGain_func()
            self.percentGain=self.percentGain_func()
            self.annualizedReturn=self.annualizedReturn_func()
        def GetStockData(self):
            print("get stock data")
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
            print("Current 52 Week High:"+str(self.share52wkhigh))
            print("Current 52 Week Low:"+str(self.share52wklow))
            print("Current Trend:"+self.trend)
        def PrintCompact2(self):
            print(" %8s %8.2f %8.2f %8.2f %8.2f %8.2f %8.2f"  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice,self.sharequantity*(self.currentshareprice - self.shareprevcloseprice),self.currentshareprice,self.shareprevcloseprice))
            
        def PrintForTxtMessage(self):
            message="Ticker: %8s $+-: %8.2f AnnlRet: %8.2f Worth:%8.2f DayChange:%8.2f"  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice,self.sharequantity*(self.currentshareprice - self.shareprevcloseprice  ))
            return  message
        def PrintCompact(self):
#            print("-----------------=======================-----------------"
#            print self.ticker+"\t"+str(self.dollarGain)+"\t"+str(self.annualizedReturn)+"\t"+str(self.sharequantity*self.currentshareprice)
            print(" %8s %8.2f %8.2f %8.2f "  % (self.ticker,self.dollarGain,self.annualizedReturn,self.sharequantity*self.currentshareprice ))
                
        def PrintColorized(self):
            print(" %10s"  % (self.ticker)),
            ColorCode10pt2f(self.dollarGain)
            ColorCode10pt2f(self.annualizedReturn)
            print("\033[49m \033[39m"),
            print(self.sharequantity*self.currentshareprice ),
            ColorCode10pt2f(self.sharequantity*(self.currentshareprice - self.shareprevcloseprice))
            #ColorCode10pt2f(self.currentshareprice)
            print("%10.2f %10.2f" %(self.currentshareprice,self.shareprevcloseprice)),
            #ColorCode10pt2f(self.shareprevcloseprice)
            print("\033[49m \033[39m") #reset color to default
                
        def getSharePrice(self):
# data format found in GetStockQutoesv2.sh
#the date goes month(jan=0) day year
            url = 'http://ichart.yahoo.com/table.csv?s=%s&' % self.ticker + \
                'f=l1' #
#we actually need to get the prev close to compute gain for the day. Wall Street doesn't compute the gain from the open, but from prev close
            url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s' %self.ticker + '&f=l1opwt7'

            days = urllib.urlopen(url).read() #lines()
            data = days[:-2].split(',') 
            if float(data[0])==0.0:
                print("Uhh bad stock ticker")
            self.currentshareprice=float(data[0])
            self.shareopenprice=float(data[1])
            self.shareprevcloseprice=float(data[2])
            temp=data[3].split(" - ")
            #print(temp,temp[0][1:],temp[1][:-1])
            self.share52wklow=float(temp[0][1:])
            self.share52wkhigh=float(temp[1][:-1])
            self.trend=data[4][7:13]
#            print(self.trend[7:13])

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

############ Main 

#use ncurses, ansi color codes


input=open("StockData.txt")

DefaultColorCoding()
PrintHeader()

cumulative=Accumulator()

for line in input:
    data=""
    if line.strip(): #skip blank lines
        if line[0]!='#': #skip comments
            data=line[:-1].split(',')
            stock=Stock(data)
#            print( stock.totalpurchaseprice, stock.commission, stock.dollarGain)
            cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain)


#            stock.PrintData()
#            stock.PrintCompact2()
            stock.PrintColorized()

            message=stock.PrintForTxtMessage()
 #           print(message)
 #            emailReport("mail.djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff",stock.PrintForTxtMessage())
#            emailReport("smtp.gmail.com",587,"nick.klosterman@gmail.com","p51mustang","NAK","5079909052@tmomail.net","testnick",stock.PrintForTxtMessage())
#            emailReport("smtp.gmail.com",587,"nick.klosterman@gmail.com","p51mustang","NAK","nick_klosterman@yahoo.com","testnick",stock.PrintForTxtMessage()) #this sends a message but there is no subject or body
#    print data
cumulative.Print()
DefaultColorCoding()

"""
emailReport("smtp.djinnius.com","587","deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly")
emailReport("smtp.djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly2")
emailReport("djinnius.com",587,"deals","backcountry","NAK","5079909052@tmomail.net","stuff","hello McFly3")
#emailReport("mail.djinnius.com",587,"dals","backctry","NAK","5079909052@tmomail.net","stuff","hello McFly")
# this guy works: emailReport("smtp.gmail.com",587,"nick.klosterman@gmail.com","p51mustang","NAK","5079909052@tmomail.net","testnick","test subjetct")

"""
