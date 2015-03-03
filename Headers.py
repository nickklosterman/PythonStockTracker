
def PrintHeader():
    """ 
    output header for 11 values currently defined and try to format the width of each to accommodate the data
    DEPRECATED
    """
    print(("%7s %10s %10s %10s %10s %10s %10s %10s %10s %10s %6s"  % ("ticker","$ gain", "ann %","% gain","Curr Worth", "Today chg$","Curr Price", "Prev Close" , "52 High","52 Low", "Trend") ))


def PrintHeader2():
    """ 
    output header for 17 values currently defined and try to format the width of each to accommodate the data
    """
    print(("%s %s %12s %12s %12s %12s %12s %12s %2s %12s %6s %12s %12s %12s %5s %12s %3s "  % ("ticker","$ gain", "ann %","% gain","Curr Worth", "Today chg $","Curr Price", "Prev Close" , "52 High","52 Low", "Trend", "Sale Tk Home","Sale Taxes","Disc4Taxes", "HiLoPct","Value if invested in SP500","Years Held") ))
