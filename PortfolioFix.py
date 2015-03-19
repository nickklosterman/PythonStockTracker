'''
I had output prices/numbers with commas in the numbers delimiting the milleniums/decades in a csv file. lukcily I padded the csv , such that no numbers touched the csv delimiting commas.
e.g. ticker , 12,345.67 , 99.2 , ....
and not 
ticker,12,345.67,99.2, ....

This program goes through and removes those commas in the prices. 
'''


import re
import sys

if len(sys.argv) > 1:
    if (sys.argv[1])!="":
        filename=sys.argv[1]

else:
    print("please enter a filename")
    exit

f=open(filename,'r')
for line in f:
    print(re.sub(',(?=[0-9]{3})','',line))

f.close
