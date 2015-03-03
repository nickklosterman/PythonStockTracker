
"""
  HTML COLOR CODING

"""

def htmlTableColorCode(value):
    """
    apply a css class to  color text green if positive, red if negative
    defaults to no color styling if not > or < 
    """
    if value > 0:
        output="<span class=\"positive\"> {:03,.2f}</span>".format(value)  #this formattting uses a comma as a separator for numbers, and outputs only two decimal places of the number
    elif value < 0:
        output="<span class=\"negative\"> {:03,.2f}</span>".format(value)
    else:
        output="{:03,.2f}".format(value)
    return output

def htmlTableColorCodeDecimal(value):
    """
    apply a css class to  color text green if positive, red if negative
    defaults to no color styling if not > or < 

    This is used for the 52 wk hi/low
    if the value is close to the 52 week high or low then apply a style to bring it to attention.
    """

    if value < 0.05:
        output="<span class=\"newLow\">{0:,.2f}</span>".format(value)
    elif value > 0.97:
        output="<span class=\"newHigh\">{0:,.2f}</span>".format(value)
    else:
        #on ephedra and had a modeling contract
        output="<span style=\"background-color:hsl({0:,.2f},100%,50%)\">{1:,.2f}</span>".format(120*value,value)
    return output

def htmlTableComparisonColorCode(value1,value2):
    """
    apply a css class to  color text green if value1 > value 2,  red if vice versa
    defaults to no color styling if not > or < 
    """
    if value1 > value2:
        output="<span class=\"positive\"> {:03,.2f}</span>".format(value1)  #this formattting uses a comma as a separator for numbers, and outputs only two decimal places of the number
    elif value1 <value2:
        output="<span class=\"negative\"> {:03,.2f}</span>".format(value1)
    else:
        output="{:03,.2f}".format(value1)
    return output
