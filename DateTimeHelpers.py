import datetime

def GetDate():
    """
    Return todays date in MM/DD/YYYY format
    """
    #dateresult = (date.today()).strftime('%x')
    return (datetime.date.today()).strftime('%x') #dateresult #(((date.today()).strftime('%x'))

def GetDateTime():
    dateTimeResult = (datetime.datetime.now()).strftime('%d/%m/%y %H:%M:%S')
    return dateTimeResult

def isLeapYear(year):
    """
    Determine if the year is a leap year
    return 1 if the year is a leap year
    """
    leapyear=0
    if year%4==0:
        leapyer=1
    return leapyear
