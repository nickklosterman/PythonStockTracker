#import pymongo
def MongoStockTable_Old(inputfilename):
    """
    """
    input=open(inputfilename)
    outputlist=[]
    data_string=json.load(input)
    print("I need to create one large dictionary of the portfolios and their contents")
    for portfolio in data_string["portfolio"]:
        if portfolio["display"] == "yes":
            cumulative=Accumulator.Accumulator()
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
            cumulative=Accumulator.Accumulator()
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
