import json
import linecache
import smtplib

import Stock as S
def Alert(inputfilename,alertPercent):
    """
    
    #better algo, compile list of uni ... um never mind. I was going to say to compile list of unique stocks and only compute 1x for each stock, but depending on when you bought, it may be a winner and loser.
    """
    input=open(inputfilename)
    data_string=json.load(input)
    print('The following stocks have dropped below your threshold.')
    for portfolio in data_string["portfolio"]:
        print('==================----------',portfolio["portfolioName"],'----------==================')
        for data in portfolio["portfolioStocks"]:
            stock=S.Stock(data)
            if stock.GetGainLoss()<(1-alertPercent):
                print(stock.ticker.upper())
#            else:
#                print(stock.GetGainLoss(),stock.ticker,(1-alertPercent))

    input.close()

def getUsernamePassword(file):
    """
    Get username and password from an external file
    the username should be on the first line, the password should be on the second line.
    """

    username=linecache.getline(file,1) #username on 1st line
    password=linecache.getline(file,2) #password on 2nd line
    return username.strip(),password.strip()  #remove the CRLF


def emailReport(Host,Port,User,Password,From,To,Subject,Message):
    try:
        User,Password = getUsernamePassword(os.path.expanduser("~/.gmaillogin"))
        server=smtplib.SMTP()
        server.connect(Host,Port)
        server.starttls()
#        server.set_debuglevel(1)   
        server.login(User,Password)
        server.sendmail(From,[To],Message)
        server.quit()
        print("Successfully sent email")
    except smtplib.SMTPException:
        print("Error: unable to send email:%s" % smtplib.SMTPException)

def txtReport(Host,User,Password,From,To,Subject,Message):
    try:
        server=smtplib.SMTP(Host)
        server.login(User,Password)
        server.sendmail(From,[To],Message)
        server.quit()
    except smtp.SMTPException:
        print("Error sending text message")
