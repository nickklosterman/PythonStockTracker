import json



import Accumulator
import DateTimeHelpers as DTH
import FileOutputHelper
import Headers as H
import Stock as S
import TerminalColorCoding as TCC
import UniqueTickers as UT



def StockTable(inputfilename,taxbracketfile):
    """
    #This methoad traverses a portfolio and outputs the performance of each stock in the portfolio
    #as well as overall performance.
    """
    input=open(inputfilename)
    UniqTickers=UT.UniqueTickers(inputfilename)
    data_string=json.load(input)
    emailReportMsg=""
    htmlOutput=" "
    jsonOutput="{ \"date\":\""+DTH.GetDate()+"\",\n \"portfolio\":["
    csvOutput=""
    for portfolio in data_string["portfolio"]:
        if portfolio["display"] == "yes":
            jsonOutput+="{\"portfolioname\":\"" + portfolio["portfolioName"]+"\", \"portfolioStocks\":["
            print('==================----------',portfolio["portfolioName"],'----------==================')
            TCC.DefaultColorCoding()
            H.PrintHeader2()
            cumulative=Accumulator.Accumulator()
            emailReportMsg+=portfolio["portfolioName"]
            for data in portfolio["portfolioStocks"]:
                data["taxBracketFile"]=taxbracketfile
                stock=S.Stock(data,UniqTickers.tickerDict[data["ticker"]])
                cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain,stock.dailyChange_func() ,stock.currentWorth_func() )
                stock.PrintColorized3() #includes theoretical "what if" invested in SP500 instead
                message=stock.PrintForTxtMessage()
                emailReportMsg+=stock.JSON()
                jsonOutput+=stock.JSON()+","
                csvOutput+=stock.CSV()+"\n"
            jsonOutput=jsonOutput.rstrip(',') 
            jsonOutput+="],"
            jsonOutput+="\n" 
            jsonOutput+="\"cumulative Result\":"+cumulative.JSONify()+"}," #will need to get rid of the last trailing , 
            emailReportMsg+=cumulative.JSONify()+",\n"
            cumulative.Print()
            TCC.DefaultColorCoding()
    jsonOutput=jsonOutput.rstrip(',') 
    jsonOutput+="] }"
    input.close()
    FileOutputHelper.WriteToDisk( FileOutputHelper.CreateOutputFilename(inputfilename,".out.json"),jsonOutput,'w')
    FileOutputHelper.WriteToDisk( FileOutputHelper.CreateOutputFilename(inputfilename,"csv"),csvOutput,'a')
    #I need to push this writing to a function call
    #output=open("jsonoutput.txt",'w')
    #output.write(jsonOutput)
    #output.close()
    return stock.getDictionary() #outputlist #emailReportMsg
