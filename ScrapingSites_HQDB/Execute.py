import sys
from Common.Working import Working

def main():
    '''
    Input:
        - URL (string): url of sitesv.service = _service need scraping (REQUIRED)
        - Out (string): Output folder (By default is the same with this file)
        - Exp (boolean): Export list Venues to file xml/txt as Script1 (Default is false)        
        Example: url=http://www.cottet.es/ out="C:\output"
 
    '''
    print "Scraping..."
    working = Working()
    #working.do(sys.argv) #Comment this line then uncomment line below, if you want     to     run     in     Eclipse/    PythonIDE
    working.do(["", "url=https://www.bucmi.com"])
    print "DONE"
    
if __name__ == '__main__':
    main()