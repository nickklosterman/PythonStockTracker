import json

import StockHelper

class UniqueTickers:
    tickerDict=dict()
    dateList=[] #used for the SP500 historical performance comparison
    """
    This methoad traverses a portfolio and outputs the performance of each stock in the portfolio
    as well as overall performance.
    """
    def __init__(self,inputfilename):
        print("To really be effective, UT needs to get the open,close,high,low,trend ...for a given ticker so that it fills in the 'blanks' that getSharePrice() does.")
        input=open(inputfilename)
        tickerList=[]
        tickerSet=set()
        data_string=json.load(input)
        for portfolio in data_string["portfolio"]:
            if portfolio["display"] == "yes":
                for data in portfolio["portfolioStocks"]:
                    #print(data["ticker"])
                    if data["ticker"] not in tickerSet:
                        tickerSet.add(data["ticker"])
                    if data["ticker"] not in self.tickerDict:
                        key=data["ticker"]
                        value=StockHelper.getSharePrice(key)
                        self.tickerDict[key]=value #I need to also store the prev close price and other data otherwise this doesn't really fulfill its purpose; Really I need to make an object for the uniqueTickers and look up into a list of those.
                        #tickerDict.setdefault(data["ticker"],default) #https://wiki.python.org/moin/KeyError
                    if data["purchaseDate"] not in self.dateList:
                        self.dateList.append(data["purchaseDate"])
        input.close()
        print(tickerSet)
