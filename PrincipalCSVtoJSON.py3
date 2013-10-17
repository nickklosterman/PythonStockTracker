#!/usr/bin/env/python
# -*- python -*- 
"""
This program takes in a CSV file that was taken from Principal.com invesetment services and outputs a JSON object ingestible by my StockTracker app.
Honestly this should ingest html as right now I'm selecting the html table copying that, pasting it into Excel. Saving that as a csv file and then ingesting that. I'd have to save off the .html anyway. so not sure which is harder/easier.
"""


import glob
import os
import csv
from math import ceil
import sys
import re #regular expression
class PrincipalImportCSVExportJSON:
    """    headerString="
    {"portfolio":
    [
    {
    "portfolioName": "TRowePrice Brokerage Rollover IRA",
    "display":"yes",
    "portfolioStocks":
    [
    "
    """
    def __init__(self,directory):
        self.fileList=""


        self.directory=directory
        #        print(self.database,self.table,self.directory)

        self.getCSVFileList()

        self.loopOverFiles()


    def getCSVFileList(self):
        os.chdir(self.directory) 
        self.fileList=glob.glob("*.csv")
        
    def tickerFromFilename(self,filename):
        return (filename.split('.'))[0]
        
            
        
    def loopOverFiles(self):
        for csvfile in self.fileList:
            
            ticker=(csvfile.split('.'))[0]
            ticker=ticker.strip()
            outpufilename=ticker+".json"
            #csvfile sure the file size isn't 0       
            if (os.stat(csvfile).st_size!=0):
                with open(csvfile,'rt') as csvFileHandle:
                    csvDataReader=csv.DictReader(csvFileHandle,delimiter=',')
                    counter=0
                    inv401k=[]
                    rothIRA=[]
                    inv401kMatch=[]
                    for row in csvDataReader:
                        if row['Contribution Type']!="ZZZZZZZZZZZZZZZZZZZZZZTotal":

                            # ActAmount=float(row['Activity Amount'].strip('$').strip('"').strip(',').strip(' '))
                            ActAmount=float(re.sub("[^\d\.]","",row['Activity Amount'])) #using regex is much handier than the above. Regular expression pattern says "anything that isn't a number or a decimal point". Anything matching that regex is replaced with "".  http://stackoverflow.com/questions/5180184/python-remove-comma-in-dollar-amount
                            date=row['Date']
                            contribution=row['Contribution Type']
                            shares=float(row['# of Shares / Unit'])
                            sharePurchasePrice=float(row['NAV / Unit Value'])
                            #print(" { \"ticker\":\"%s\", \"shares\":%s, \"totalPurchasePrice\":%f, \"purchaseDate\": \"%s\", \"commissionToBuy\":0, \"commissionToSell\":0, \"contributionType\":\"%s\"}," % ( ticker,shares,ActAmount,date,contribution))
                            output=(" { \"ticker\":\"%s\", \"shares\":%s, \"totalPurchasePrice\":%f, \"purchaseDate\": \"%s\", \"commissionToBuy\":0, \"commissionToSell\":0, \"contributionType\":\"%s\"}" % ( ticker,shares,ActAmount,date,contribution))
                            if (counter%4==0):
                                #print("401(k)")
                                inv401k.append(output)
                            elif (counter%4==1):
                                #print("Roth IRA")
                                rothIRA.append(output)
                            elif (counter%4==2):
                                #print("Employer Match 401(k)")
                                inv401kMatch.append(output)
                            elif (counter%4==3):
                                print("Total")
                            counter+=1                            
                    print("  {\"portfolio\":    [")
                    print(" {    \"portfolioName\": \"%s\", \"display\":\"yes\",  \"portfolioStocks\": [" %("Principal 401k"))
                    listLength=(len(inv401k))
                    for counter,item in enumerate(inv401k):
                        print(item,end="")
                        if counter<listLength-1:
                            print(",")
                    print("] }, ")
                    print(" {    \"portfolioName\": \"%s\", \"display\":\"yes\",  \"portfolioStocks\": [" %("Principal Roth IRA"))
                    
                    listLength=(len(rothIRA))
                    for counter,item in enumerate(rothIRA):
                        print(item,end="")
                        if counter<listLength-1:
                            print(",")
                    print("] }, ")
                    print(" {    \"portfolioName\": \"%s\", \"display\":\"yes\",  \"portfolioStocks\": [" %("Principal 401k Emplyer Match"))
                    
                    listLength=(len(inv401kMatch))
                    for counter,item in enumerate(inv401kMatch):
                        print(item,end="")
                        if counter<listLength-1:
                            print(",")
                    print("]} ]}")
        


#def main
import getopt

if 1:
    directory="PrincipalCSVDataFiles"
try:
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'i:o:l:t:d:f:', ['--input=',
                                                                          '--output=',
                                                                          '--loginfile=',
                                                                          '--table=',
                                                                          '--database=',
                                                                          '--format='
                                                                        ])
except getopt.GetoptError as err:
    # print help information and exit:                                                                        
    print(err) # will print something like "option -a not recognized"                                         
        #usage()                                                                                                  
    sys.exit(2)

for opt, arg in options:
    if opt in ('-o', '--output'):
        outputfilename = arg
    elif opt in ('-i', '--input'):
        inputfilename = arg
    elif opt in ('-t', '--table'):
        table = arg
    elif opt in ('-d', '--database'):
        database = arg
    elif opt in ('-f', '--format'):
        outputFormat = arg
    elif opt == '--version':
        version = arg
        
Importer=PrincipalImportCSVExportJSON(directory)
