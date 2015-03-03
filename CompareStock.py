
import TerminalColorCoding as TCC

class CompareStock:
    """
    Class to compare two stocks performance and output a small summary comparison
    """
    def __init__(self,stockdata1,stockdata2):
        """
        #create two ministock objects  
        #is there a better way to utilize objects? init the object and pass it in and copy or deepcopy it? Hmm that doesn't seem right bc then there is the original hanging out there that is just taking up space.
        """
        self.Stock1=stockdata1
        self.Stock2=stockdata2

    def printComparison(self):
        """
        Prints purchase date, total purchase price, ticker of stock1 , gain/loss of stock 1, ticker of stock 2, gain/loss of stock 2, and then outputs stock1 vs stock2 values and highlights which one would've produced better gains.
        """
        print("%5s %6.2f %5s"  % (self.Stock1.GetPurchaseDateYYYY_MM_DDFormatted(),self.Stock1.GetTotalPurchasePrice(),self.Stock1.GetTicker()),end=' ')
        TCC.ColorCode10pt2fRelative(self.Stock1.GetGainLoss(),1)
        TCC.DefaultColorCoding() 
        print(" %5s " % (self.Stock2.GetTicker()), end=' ')
        TCC.ColorCode10pt2fRelative(self.Stock2.GetGainLoss(),1)
        TCC.DefaultColorCoding() 
        self.printBest()

    def printBest(self):
        """
        Compare two stocks gains/losses and output their values color coding the better investment of the two.
        """
        total1=self.Stock1.GetTotalPurchasePrice()*self.Stock1.GetGainLoss()
        total2=self.Stock1.GetTotalPurchasePrice()*self.Stock2.GetGainLoss()
        TCC.ColorCode10pt2fRelative(total1,total2)
        TCC.DefaultColorCoding()
        print( " vs ", end= ' ')
        TCC.ColorCode10pt2fRelative(total2,total1)
        TCC.DefaultColorCoding()
        print("")
