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

class PrincipalImportCSVExportJSON:
    
    def __init__(self,directory):
        self.fileList=""


        self.directory=directory
        #        print(self.database,self.table,self.directory)

        self.getCSVFileList()

        self.loopOverFiles()


    def getCSVFileList(self):
        os.chdir(self.directory) 
        self.fileList=glob.glob("*.csv")
            
        
    def loopOverFiles(self):
        for csvfile in self.fileList:
            print(csvfile)
            ticker=(csvfile.split('.'))[0]
            ticker=ticker.strip()
            #csvfile sure the file size isn't 0       
            if (os.stat(csvfile).st_size!=0):
                with open(csvfile,'rt') as csvFileHandle:
                    csvDataReader=csv.DictReader(csvFileHandle,delimiter=',')
                    counter=0
                    for row in csvDataReader:

                        if row['Contribution Type']!="ZZZZZZZZZZZZZZZZZZZZZZTotal":
                            if (counter%4==0):
                                print("401(k)")
                            elif (counter%4==1):
                                print("Roth IRA")
                            elif (counter%4==2):
                                print("Employer Match 401(k)")
                            elif (counter%4==3):
                                print("Total")
                            counter+=1                            
                            ActAmount=float(row['Activity Amount'].strip('$').strip('"').strip(',').strip(' '))
                            date=row['Date']
                            contribution=row['Contribution Type']
                            shares=float(row['# of Shares / Unit'])
                            sharePurchasePrice=float(row['NAV / Unit Value'])
                            print(" { \"ticker\":\"%s\", \"shares\":%s, \"totalPurchasePrice\":%f, \"purchsaeDate\": \"%s\", \"commissionToBuy\":0, \"commissionToSell\":0, \"contributionType\":\"%s\"}," % ( "rpmgx",shares,ActAmount,date,contribution))
        


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
