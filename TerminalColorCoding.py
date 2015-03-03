
"""
  ANSI COLOR CODING OF TERMINAL 

use ansi color codes to color fg and bg : http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html; curses is an alternative
"""

def DefaultColorCoding():
    """
    Use ansi color codes to set the terminal output to the default color coding
    """
    print(("\033[49m \033[39m "), end=' ') #set to default color coding, suppress newline


def ColorCode10pt2f(number):
    """
    use ansi color code to color text green if positive, red if negative
    color coding stays until the ansi terminal is set back to the default color coding. Call DefaultColorCoding()
    output with two decimal places of precision
    """
    if number>0: 
        print(("\033[32m %10.2f"% (number)), end=' ') #suppress newline
    else:
        print(("\033[31m %10.2f"% (number)), end=' ') 


def ColorCode10pt2fRelative(number,comparedto):
    """
    use ansi color code to color text green if value1 greater than value2, red if less than
    color coding stays until the ansi terminal is set back to the default color coding. Call DefaultColorCoding()
    output with two decimal places of precision
    """
    if number>comparedto: 
        print(("\033[32m %10.2f"% (number)), end=' ') #suppress newline
    else:
        print(("\033[31m %10.2f"% (number)), end=' ') 


def ColorCode8s(string):
    """
    use ansi color code to display string as red text
    color coding stays until the ansi terminal is set back to the default color coding. Call DefaultColorCoding()
    Currently not used anywhere
    """
    print(("\033[31m %8s"% (string)))
