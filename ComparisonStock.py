import TerminalColorCoding as TCC
import MiniStock as MS
class ComparisonStock:
    def __init__(self,stockdata1,stockdata2):
#create two ministock objects  
#is there a better way to utilize objects? init the object and pass it in and copy or deepcopy it? Hmm that doesn't seem right bc then there is the original hanging out there that is just taking up space.
        self.miniStock1=MS.MiniStock(stockdata1)
        self.miniStock2=MS.MiniStock(stockdata2)
    def Header(self):
        """
        """
        print("%5s %s %s %s %s %s %s %s" % ("buy date","init inv","tickr","gain/loss","tickr","gain/loss","value1","value2" ))
    def printComparison(self):
        """
        
        """
        self.Header()
        print("%5s %6.2f %5s"  % (self.miniStock1.GetPurchaseDate(),self.miniStock1.GetTotalPurchasePrice(),self.miniStock1.GetTicker()),end=' ')
        TCC.ColorCode10pt2fRelative(self.miniStock1.GetGainLoss(),1)
        TCC.DefaultColorCoding() 
        print(" %5s " % (self.miniStock2.GetTicker()), end=' ')
        TCC.ColorCode10pt2fRelative(self.miniStock2.GetGainLoss(),1)
        TCC.DefaultColorCoding() 
        self.printBest()

    def printBest(self):
        """
        """
        total1=self.miniStock1.GetTotalPurchasePrice()*self.miniStock1.GetGainLoss()
        total2=self.miniStock1.GetTotalPurchasePrice()*self.miniStock2.GetGainLoss()
        TCC.ColorCode10pt2fRelative(total1,total2)
        TCC.DefaultColorCoding()
        print( " vs ", end= ' ')
        TCC.ColorCode10pt2fRelative(total2,total1)
        TCC.DefaultColorCoding()
        print("")
