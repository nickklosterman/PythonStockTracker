#!/usr/bin/python3

import os #for converting ~ -> users home directory
import json

def ExtractPortfolioStocks(inputfilename):
    input=open(inputfilename)
    data_string=json.load(input)
    stockz=[]
    for portfolio in data_string["portfolio"]:
        for stock in portfolio["portfolioStocks"]:
            stockz.append(stock["ticker"])
    myset=set(stockz) #create unique set of tickers http://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python
   
    sortedTickers =sorted(myset, key=lambda item: (int(item.partition(' ')[0])
                                                   if item[0].isdigit() and item[1].isdigit() else float('inf'),item)) #stolen from:http://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
    for ticker in sortedTickers:
        print(ticker)
    input.close()

def usage():
    print("python StockTrackerJSON  [ -c/--comparison, -i/--input=portfolio.json -s/--stocktable -e/--email -w/--web-html]")
    print("-i/--input=portfolio.json")

"""
############ Main 
"""

from  textwrap import TextWrapper
wrapper =TextWrapper()
wrapper.width=190 #set text wrapping width manually otherwise if drag terminal to full width python doesn't write text out the full width

import getopt 
import sys


print(sys.argv[1:])
try:
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'i:', [ 'input='
                                                                ])
except getopt.GetoptError as err:
    # print help information and exit:                                                                        
    print( str(err)) # will print something like "option -a not recognized"                                         
    usage()                                                                                                  
    sys.exit(2)

for opt, arg in options:
    if opt in ('-i', '--input'):
        inputfilename=arg
    else:
        assert False, "unhandled option"

ExtractPortfolioStocks(inputfilename)

