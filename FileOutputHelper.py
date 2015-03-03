def CreateOutputFilename(inputfilename,extension):
    """
    Strip out the path and extract the base of the inputfilename for reuse as the base of the outputfilename

    I feel like I could have that second argument be a list of things to append dot separated.
    """
    filenameWithPath=(inputfilename.split('/'))
    print(filenameWithPath)
    filename=(filenameWithPath[len(filenameWithPath)-1]).split('.')
    print(filename)
    if (extension[0]=="."):
        outputfilename=filename[0]+extension
    else:
        outputfilename=filename[0]+"."+extension
    print(outputfilename)
    return outputfilename

def WriteToDisk(filename,data,mode):
    output=open(filename,mode)
    output.write(data)
    output.close()
