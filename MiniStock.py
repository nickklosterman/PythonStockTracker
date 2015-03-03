import datetime
import StockHelper
class MiniStock:
    """
    class to allow easy comparison to SP500,Nasdaq performance over same period
    I really need an all purpose method to do comparisons
    """
    def __init__(self,data):
        self.ticker=data['ticker']
        temp=data["purchaseDate"].split('/')
        self.purchaseDate=datetime.datetime(int(temp[2]),int(temp[0]),int(temp[1]))
        self.totalPurchasePrice=data['totalPurchasePrice']
        self.commissionToBuy=data['commissionToBuy']
        #self.unitPriceAtPurchase=get_historical_prices_plus_one_day(self.ticker,(self.purchaseDate.strftime('%Y%m%d'))) #NO LONGER USING this version since IBD lists are published the night before their list date, so you could purchase at the open.
        self.unitPriceAtPurchase=StockHelper.get_historical_price(self.ticker,(self.purchaseDate.strftime('%Y%m%d')))
        self.unitPriceAtPresent=StockHelper.getSharePrice(self.ticker)

       
    def GetGainLoss(self):
        return float(self.unitPriceAtPresent)/float(self.unitPriceAtPurchase)
    def GetProfit(self):
        return self.gainloss*(self.totalPurchasePrice-self.commissionToBuy)-(self.totalPurchasePrice-self.commissionToBuy)
    def GetTicker(self):
        return self.ticker
    def GetPurchaseDate(self):
        return  self.purchaseDate.strftime('%Y-%m-%d')
    def GetTotalPurchasePrice(self):
        return self.totalPurchasePrice
