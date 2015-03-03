#!/usr/bin/python3
#usage:
# python StockTrackerJSON.py -i AllPortfolios.json -a 8 #alerts if share price is 8% lower than when bought.
# python StockTrackerJSON.py -i AllPortfolios.json -s
# python StockTrackerJSON.py -i AllPortfolios.json -c
# python3 ~/Repo/Github/PythonStockTracker/StockTrackerJSON.py --input ~/Repo/BB/configfiles/StockTrackerJSON/AllPortfolios.json --tax-bracket-file  ~/Repo/Github/PythonStockTracker/TaxBracket.txt -w -s


import Accumulator
import DateTimeHelpers as DTH
import FileOutputHelper
import HTMLTable as HT
import MongoStockTable as MST
import Stock as S
import StockHelper
import StockTable as ST
import TerminalColorCoding as TCC
import UniqueTickers as UT

"""
Any note of 'tax' in this program uses tax algorithms for US taxes. For other countries adjust accordingly
As tax laws constantly change, these calculations should be taken with a huge grain of salt.
"""
    
def getSharePriceFromDatabase(ticker):
    import sqlite3
    connection=sqlite3.connect(database)
    cursor=connection.cursor()
    Query='SELECT Close FROM '+ticker+' LIMIT 1 '
    cursor.execute(Query)
    while True:
        row=cursor.fetchone()
        print(row)
        if row[1] is  None:
            return -1
        return row

def PrintBanner(input):
    """
    print banner text
    used to ouput the portfolio/filename that is being processed
    """ 
    print("#######################################################################")
    print('                          ',input)
    print("#######################################################################")

'''
class PortfolioAccumulator:
    def __init__(self):
        self.
hmm I suppose I could use an accumulator to accumulate for all teh individual portfolios
'''


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
    NOT USED
    """
    temp=MMDDYYYYDate.split('/')
    tempdate=datetime.date(int(temp[2]),int(temp[0]),int(temp[1]))
    return tempdate.strftime("%Y%m%d")
    

#using the miniStock is inefficient bc you are repeatedly going out to the web to pull the quotes. You really want to use the Stock Objects, pass them in and then do the comparison.




#TODO: create Portfolio object and have a total for the entire portfolio
#todo: trend line of +-+-++ for last few days worth of trading,
#generic line for an index. as comparison

def usage():
    print("python StockTrackerJSON  [ -c/--comparison, -i/--input=portfolio.json -s/--stocktable -e/--email -w/--web-html]")
    print("-a/--alert=X Only output those stocks whose value has dropped below X % of the purchase price.")
    print("-c/--comparison Output performance comparing each stock to all the others in the portfolio")
    print("-e/--email=joe.schmoe@email.org Email the results to user joe.schmoe@email.org")
    print("-i/--input=portfolio.json")
    print("-m/--mongo Output data to local MongoDB instance AllPortfolios table")
    print("-s/--stocktable Output the stock table ")
    print("-t/--tax-bracket-file Tax bracket file to use and parse. Defaults to (~/Git/PythonStockTracker) ./TaxBracket.txt")
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

debugflag = False
comparisonflag=False
stocktableflag=False
alertflag=False
alertPercent=0.8
destinationemail="foo.bar@example.com"
database="YahooHistoricalDatabase.sqlite3"
databaseflag=False
mongoflag=False
htmltableflag=False
taxBracketFile="TaxBracket.txt"
inputfilename=""
print(sys.argv[1:])
#pretty much straight from : http://docs.python.org/release/3.1.5/library/getopt.html
#took me a while to catch that for py3k that you don't need the leading -- for the long options
#sadly optional options aren't allowed. says it in the docs :( http://docs.python.org/3.3/library/getopt.html
try:
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'a:e:d:t:csi:mw', ['alert=',
                                                                          'compare',
                                                                          'database',
                                                                          'email=',
                                                                          'input=',
                                                                          'mongo',
                                                                          'stocktable',
                                                                          'tax-bracket-file=',
                                                                          'web-html-table'
                                                                ])
except getopt.GetoptError as err:
    # print help information and exit:                                                                        
    print( str(err)) # will print something like "option -a not recognized"                                         
    usage()                                                                                                  
    sys.exit(2)

for opt, arg in options:
    if opt in ('-a', '--alert'): #check for stocks where loss is > 8 %
        alertflag=True
        try:
            alertPercent=float(arg) #will it break if an opt isn't specified?
        except ValueError:
            alertPercent=8
        if alertPercent > 1:
            alertPercent=alertPercent/100;
    elif opt in ('-c', '--compare'):
        comparisonflag=True
    elif opt in ('-d', '--database'):
        database=arg
        databaseflag=True
    elif opt in ('-e', '--email'):
        destinationemail=arg
    elif opt in ('-i', '--input'):
        inputfilename=arg
    elif opt in ('-m', '--mongo'):
        mongoflag=True
    elif opt in ('-s', '--stocktable'):
        stocktableflag=True
    elif opt in ('-t', '--tax-bracket-file'):
        taxBracketFile=arg
    elif opt in ('-w', '--web-html-table'):
        htmltableflag=True
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
if (inputfilename==""):
    sys.exit(2)
    
PrintBanner(inputfilename)

"""
#this is super inefficient. I should go out and construct the data for each stock / portfolio and then run the stats, using those objects. I shouldn't go out and get the yahoo data for each function
#TODO make this efficient. eliminate the unnecessary slow calls to yahoo
UniqTickers=UT.UniqueTickers(inputfilename)
print("TickerDict")
print(UniqTickers.tickerDict)
print("DateList")
print(UniqTickers.dateList)
"""
if debugflag == True:
    stocktableflag = False
    comparisonflag = False
    alertflag = False
    htmltableflag = False
    mongoflag = False

print("create a --compare-to flag which lets you compare the performance to any ticker, then append this compare to data to an auxiliary table. this will hold the historic values so that you aren't constantly looking these up. they arne't going to change so we should preprocess looking for this table and if not generate one and append it ")

#this is kinda awful as the outputs should be separated from the acutal objects themselves. if I do :
#python3 ~/Repo/Github/PythonStockTracker/StockTrackerJSON.py --input ~/Repo/BB/configfiles/StockTrackerJSON/AllPortfolios.json --tax-bracket-file  ~/Repo/Github/PythonStockTracker/TaxBracket.txt -w -s
# I'm doing double duty as the same data is downloaded and the same data is being recreated twice. :(

if stocktableflag:
    ST.StockTable(inputfilename,taxBracketFile)
if comparisonflag:
    CP.ComparePortfolio(inputfilename)
if alertflag:
    Alert(inputfilename,alertPercent)
if htmltableflag:
    HT.HTMLTable(inputfilename,taxBracketFile)
if mongoflag:
    MST.MongoStockTable(inputfilename)
#    MongoSave(StockTable(inputfilename))#.JSONify())
#    MongoSave("{ 'name':'bob', 'hair':'bald'}")#.JSONify())
print("") #otherwise the prompt isn't on a new line


            
