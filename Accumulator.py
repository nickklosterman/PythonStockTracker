import json
class Accumulator:
    """
    Class used to accumulate the gains and losses across the entire portfolio
    
    """
    def __init__(self):
        self.totalpurchaseprice=0.0
        self.totalcommission=0.0
        self.totaldollargain=0.0
        self.totallosses=0.0
        self.totalgains=0.0
        self.dailydollargain=0.0
        self.dailytotallosses=0.0
        self.dailytotalgains=0.0
        self.portfolioworth=0.0
        self.dailypercentchange=0.0
    def Add(self, purchaseprice, commission, dollargain,dailygain,currentworth):
        """
        Add data to the appropriate fields for the accumulator
        """
        self.totalpurchaseprice+=purchaseprice
        self.totalcommission+=commission
        self.totaldollargain+=dollargain
        if dollargain < 0.0:
            self.totallosses+=dollargain
        else:
            self.totalgains+=dollargain
        if dailygain < 0.0:
            self.dailytotallosses+=dailygain
        else:
            self.dailytotalgains+=dailygain
        self.portfolioworth+=currentworth
    def CalculateDailyPercentChange(self):
        """
        Calculate the daily percentage change of the portfolio up to that time
        
        """
        # print(self.portfolioworth)
        # print(self.dailytotallosses)
        # print(self.dailytotalgains )
        # print(self.portfolioworth-self.dailytotallosses-self.dailytotalgains )
        denominator = self.portfolioworth-self.dailytotallosses-self.dailytotalgains
        #prevent division by zero
        if denominator != 0:
            self.dailypercentchange=((self.dailytotalgains+self.dailytotallosses)/denominator*100)


    def Print(self):
        """
        Print the Accumulator fields
        gains field is ansi colored green
        losses field is ansi colored red
        """
        print("")
        print(("%22s %10.2f" % ("Total Purchase Price:",self.totalpurchaseprice)))
        print(("%22s %10.2f" % ("Total Commission Paid:",self.totalcommission)))
        print(("%22s %10.2f" % ("Total Gain/Loss:",self.totaldollargain))) #this is just the total of self.totallosses+self.totalgains
        print(("%27s %10.2f %s" % ("Total Dollar Losses:\033[31m" ,self.totallosses, " \033[39m" )))
        print(("%27s %10.2f %s" % ("Total Dollar Gains:\033[32m" ,self.totalgains, " \033[39m" )))
        print(("%22s %10.2f" % ("Daily Losses:",self.dailytotallosses)))
        print(("%22s %10.2f" % ("Daily Gains:",self.dailytotalgains)))
        print(("%22s %10.2f" % ("Daily Change:",self.dailytotalgains+self.dailytotallosses)))
        self.CalculateDailyPercentChange()

        print(("%22s %10.2f" % ("Daily % Change:", self.dailypercentchange )))
        print(("%22s %10.2f" % ("Portfolio Worth:",self.portfolioworth)))



    def JSONify(self):
        """
        Create and return the Accumulator fields as a json object
        """
        #self.CalculateDailyPercentChange()
        jsonData = json.dumps({
            "Total Purchase Price":self.totalpurchaseprice,
            "Total Commission Paid":self.totalcommission,
            "Total Gain/Loss":self.totaldollargain,
            "Total Dollar Losses":self.totallosses, 
            "Total Dollar Gains":self.totalgains, 
            "Daily Losses":self.dailytotallosses,
            "Daily Gains":self.dailytotalgains,
            "Daily Change":self.dailytotalgains+self.dailytotallosses,
            "Daily % Change": self.dailypercentchange,
            "Portfolio Worth":self.portfolioworth
        } )
        return jsonData

    def CSV(self):
        """
        Output Accumulator fields as csv

        """
        separator=","
        output="""{0}{1:,.2f}{0} 
        {2:,.2f} 
        {0}{3:,.2f}
            {0}{4:,.2f}
            {0}{5:,.2f}
            {0}{6:,.2f}
            {0}{7:,.2f}
            {0}{8:,.2f}
            {0}{9:.2f}
            {0}{10:,.2f} 
 """.format(separator,
self.totalpurchaseprice,
self.totalcommission,
self.totaldollargain,
self.totallosses,
 self.totalgains,
 self.dailytotallosses,
self.dailytotalgains,
self.dailytotalgains+self.dailytotallosses,
self.dailypercentchange,
self.portfolioworth)
        return output

    def HTMLTableOutput(self):
        """
        Output Accumulator fields in html to be added to a table
        
        used as prep to output portfolio / stock data  using createHTMLOutput()
        """
        separator="</th><td>"
        endseparator="</td><td colspan=\"12\"></tr><tr><th colspan=\"4\">"
        output="""<tr><th colspan=\"4\">Total Purchase Price {0} {2:,.2f} {1}             
        Total Commission Paid{0}{3:,.2f}{1}
            Total Gain/Loss{0}{4:,.2f}{1}
            Total Dollar Losses{0}{5:,.2f}{1}
            Total Dollar Gains{0}{6:,.2f}{1}
            Daily Losses{0}{7:,.2f}{1}
            Daily Gains{0}{8:,.2f}{1}
            Daily Change{0}{9:,.2f}{1}
            Daily % Change{0}{10:.2f}{1} 
            Portfolio Worth{0}{11:,.2f} </td><td colspan=\"12\"></tr>
 """.format(separator,endseparator,
self.totalpurchaseprice,
self.totalcommission,
self.totaldollargain,
self.totallosses,
 self.totalgains,
 self.dailytotallosses,
self.dailytotalgains,
self.dailytotalgains+self.dailytotallosses,
self.dailypercentchange,
self.portfolioworth)
        return output
