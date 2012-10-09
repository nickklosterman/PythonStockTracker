'''
just a sandbox file to learn how to use the json parser and how to access the resulting datastructure.
in teh end it just is a dictionary that you need to traverse through.
'''
import json,sys,os.path
from pprint import pprint
i=1
if os.path.isfile(sys.argv[i]):
    inputfilename=sys.argv[i]
i+=1
input=open(inputfilename)
data_string=json.load(input)
#print(data_string) #works
#print(data_string["portfolio"][1]["portfolioStocks"]) #works
#print(len(data_string)) #works
#pprint(data_string) #works
#print("JSON:",data_string) #works
for portfolio in data_string["portfolio"]:
    print(portfolio["portfolioName"])
    #for key,val in portfolio["portfolioStocks"].items():    
     #   print(key)


    for ele in portfolio["portfolioStocks"]:
        print(ele)
     #   print(ele["ticker"],ele["purchaseDate"],ele["totalPurchasePrice"],ele["commissionToBuy"],ele["commissionToSell"],ele["shares"])
'''        print(ele["ticker"])
        print(ele["purchaseDate"])
        print(ele["totalPurchasePrice"])
        print(ele["commissionToBuy"])
        print(ele["commissionToSell"])
   '''     
'''
    for ele in portfolio["portfolioName"]:
        print(ele) #prints the portfolioName 1 character at a time.
'''

#print(len(data_string)) #works
#print(len(data_string[0]))
#print(data_string["portfolio"][1]["portfolioStocks"][0]) #works

#-------------
#FML:data_string is a dict but data_string["portfolio"]and data_string.items() are a list
for k,v in data_string.items():
    #print(k,v)
    for k2,v2 in v.items():
        print(k2,v2)
    

input.close()
