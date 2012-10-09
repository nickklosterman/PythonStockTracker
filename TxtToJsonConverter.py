'''
This program is meant to convert a flat text file that contains 1 entry per line of :
ticker,shares,totalpurchaseprice,purchaseDate(mm/dd/yy),commissiontoBuy,commissiontoSell
to valid json.
e.g.:
aapl,142,1482.56,10/23/2000,31.50,7 --> {"ticker":"aapl","shares":142,"totalPurchasePrice":1482.56,"purchaseDate":"10/23/2000","commissionToBuy":31.50,"commissionToSell":7}
these json strings can then be pasted into AllPortfolios.json for parsing by StockTrackerJSON.py

'''
def PrintStockFormat(keys,values,lastline):
    #print warning if data not long enough
    if (len(keys)!=len(values)):
        print("unbalanced keys values pair")
    outputstring="{"
    zipped=zip(keys,values) # The returned list is truncated in length to the length of the shortest argument sequence from: http://docs.python.org/library/functions.html?highlight=zip#zip
    zippedlen=len(keys)#len(zipped) zip'ed item doesn't have len()

    for i,mytuple in enumerate(zipped):#http://stackoverflow.com/questions/126524/iterate-a-list-with-indexes-in-python
        if i!=zippedlen-1:
            if i==3 or i==0: #date,ticker field needs to be quoted for JSON
                outputstring+=mytuple[0]+':"'+mytuple[1]+'",'
            else:
                outputstring+=mytuple[0]+':'+mytuple[1]+','
        else:
            outputstring+=mytuple[0]+':'+mytuple[1]
    if lastline!=True:
        outputstring+="},"#outputting a , on the last element of an array will break the json.
    else:
        outputstring+="}"
    print(outputstring)

def Formatter(inputfilename):
    input=open(inputfilename)
#I count the lines in the file that are valid(not blank or comments) so that I can accurately determine which line is the last line. This is needed to create valid JSON as the last element in an array can't have a trailing comma
    linecounter=0;
    for line in input:
        if line.strip() and line[0]!='#': #skip blank lines
            linecounter+=1
    input=open(inputfilename) #need to reload file since we prev ran to end of it.
    linenumber=0
    for line in input:
        linenumber+=1
        if line.strip() and line[0]!='#': #skip blank lines
            #        if line.strip(): #skip blank lines
            #            if line[0]!='#': #skip comments
            data=line[:-1].split(',')
            if linenumber==linecounter:
                PrintStockFormat(header,data,True)
            else:
                PrintStockFormat(header,data,False)
    input.close()

header=['"ticker"','"shares"','"totalPurchasePrice"','"purchaseDate"','"commissionToBuy"','"commissionToSell"']
#header=['"ticker"','"shares"','"totalPurchasePrice"','"purchaseDate"','"commissionToBuy"','"commissionToSell"','"fake"'] #too long
#header=['"ticker"','"shares"','"totalPurchasePrice"','"purchaseDate"','"commissionToBuy"'] #too short

#--------------------MAIN------------
import json,sys,os.path

i=1
while i< len(sys.argv):
    if os.path.isfile(sys.argv[i]):
        inputfilename=sys.argv[i]
    i+=1
    Formatter(inputfilename)
