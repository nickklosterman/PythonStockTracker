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
            stockz.append(S.Stock(stock))
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


def printCompareHeader():
    print("  buy date  InitInv  tickr  gain/loss     tickr      gain/loss       value1            value2" )
