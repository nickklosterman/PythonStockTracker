import datetime
import json

import Accumulator
import Stock as S
import UniqueTickers as UT
class HTMLTable:
    """
    This methoad traverses a portfolio and outputs the performance of each stock in the portfolio
    as well as overall performance.
    """
    def __init__(self,inputfilename,taxbracketfile):
        input=open(inputfilename)
        UniqTickers=UT.UniqueTickers(inputfilename)
        portfolioTabsList=[]
        portfolioStockDataList=[]
        portfolioTabContentsList=[]
        filenameWithPath=(inputfilename.split('/'))
        print(filenameWithPath)
        filename=(filenameWithPath[len(filenameWithPath)-1]).split('.')
        print(filename)
        outputfilename=filename[0]+".html"
        print(outputfilename)
        data_string=json.load(input)
        htmlOutput=" "
        for portfolio in data_string["portfolio"]:
            if portfolio["display"] == "yes":
                portfolioName=portfolio["portfolioName"]
                portfolioTabsList.append(portfolio["portfolioName"])
                cumulative=Accumulator.Accumulator()
                for data in portfolio["portfolioStocks"]:
                    print(UniqTickers.tickerDict[data["ticker"]])
                    data["taxBracketFile"]=taxbracketfile
                    stock=S.Stock(data,UniqTickers.tickerDict[data["ticker"]])
                    cumulative.Add(stock.totalpurchaseprice, stock.commission_to_buy, stock.dollarGain,stock.dailyChange_func() ,stock.currentWorth_func() )
                    portfolioStockDataList.append(stock.htmlTableRowOutput())
                portfolioTabContentsList.append(createPortfolioTable(portfolioName,portfolioStockDataList,cumulative.HTMLTableOutput())) 
            portfolioStockDataList=[] #clear the list for the next portfolio
        input.close()
        output=open(outputfilename,'w')
        output.write(createHTMLOutput(filename[0],portfolioTabsList,portfolioTabContentsList))
        output.close()
        print("Output written to ",outputfilename,".")

def createPortfolioTable(name,dataList,cumulativeData):
    """
    Given a portfolio name, a list of stock data , and a list of cumulative portfolio data, create an html table to display the data
    """
    startText='<table border="2" class="hoverTable"><caption>'
    output=startText+name+"</caption>"
    header="""<tr><th>Ticker</th><th>
   $ gain</th><th>
    Ann %</th><th>
    % gain</th><th>
    Curr Worth</th><th>
    Today chg $</th><th>
    Curr Price</th><th>
    Prev Close</th><th>
    52 High</th><th>     
    52 Low </th><th>
    Trend</th><th>
    Sale Tk Home</th><th> 
    Sale Taxes</th><th> 
    Disc4Taxes</th><th>
    HiLoPct</th><th>
    Value if invested in SP500</th><th> 
    Years Held </th></tr>"""
    output+=header
    for item in dataList:
        output+=item
    output+=cumulativeData+'</table>'
    return output

def createHTMLOutput(portfolioName,portfolioNameList,portfolioContentList):
    """
    create an html webpage from a list of portfolio names, and their performance data in html
    """
    runDate=datetime.datetime.now()
    start="""<html lang="en"> 
    <head>
    <meta HTTP-EQUIV="Refresh" CONTENT="300" charset="utf-8" />
    <title> %s %s </title>
    <link rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
    <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
    <!-- <script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script> uncomment this to go back to using the jquery tabs-->
    <link rel="stylesheet" href="/resources/demos/style.css" />
    <script>
    $(function() {
    $( "#tabs" ).tabs();
    });
    </script>
    <style type="text/css">
/*highlight when hover on table row*/
.hoverTable tr:hover { background-color: #b8d1f3 }
/* For simplicity's sake I keep all the styles in the file, otherwise if I have a shortcut, I would need to copy the style file over or point to it specifically (point to a style file that is symlinked to the file in the git repo) */
    .negative1 {color:red }
    .negative {background-color:tomato }
    .positive1 {color:springgreen }
    .positive {background-color:springgreen }
    .middle {background-color:yellow }
    td {text-align:right}
/*Animation Prefs*/
@-webkit-keyframes pulseHigh {
      0%% {background-color:  hsl(80,100%%,50%%);}
     25%% {background-color:  hsl(100,100%%,50%%);}
     50%% {background-color:  hsl(120,100%%,50%%);}
     75%% {background-color:  hsl(140,100%%,50%%);}
     100%% {background-color: hsl(140,100%%,100%%);}
}
@-webkit-keyframes pulseLow {
      0%% {background-color: hsl(320,100%%,50%%);}
     25%% {background-color: hsl(340,100%%,50%%);}
     50%% {background-color: hsl(360,100%%,50%%); }
     75%% {background-color: hsl(000,100%%,50%%); }
     100%% {background-color:hsl(000,100%%,0%%);}
}
.newHigh {
-webkit-animation: pulseHigh 2s infinite alternate;
}
.newLow {
-webkit-animation: pulseLow 2s infinite alternate;
}

    </style>
    </head>
    <body>
    """ % (portfolioName,runDate)
    end='</div></body></html>'
    tabs=jqueryUITabs(portfolioNameList)
    content=tabContent(portfolioContentList)
    output=start+tabs+content+end
    return output



def jqueryUITabs(tabList):
    """
    Given a list of portfolio names, create a set of tabs for jqueryUI tab usage
    """
    startText="""<div id="tabs"> 
    <ul>"""
    endText='</ul>'
    itemStart='<li><a href="#tabs-'
    itemEnd='</a></li>'
    output=startText
    for counter,item in enumerate(tabList):
        output+=itemStart+str(counter)+"\">"+item+itemEnd
    output+=endText
    return output

def tabContent(tabList):
    """
    Given a list of html elements, create the tab contents to be displayed with the jqueryUI tabs.
    """
    start='<div id="tabs">'
    startText='<div id="tabs-'
    endText='</div>'
    output=start
    for counter,item in enumerate(tabList):
        output+=startText+str(counter)+"\">"+item+endText
    return output
    
