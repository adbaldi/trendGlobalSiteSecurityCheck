#!/bin/env python3

import re
import sys
import argparse
from os import path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options



def checkSite (_site,_debug):
    
    _options = Options()
    _options.headless = True

    if _debug:
        _options.headless = False
    
    _driver = webdriver.Firefox(options=_options)
    _driver.implicitly_wait(20)
    _driver.get('https://global.sitesafety.trendmicro.com/index.php')
    
    assert "Site Safety" in _driver.title
    
    _urlname = _driver.find_element_by_name("urlname")
    _urlname.clear()
    _urlname.send_keys(_site)
    _urlForm = _driver.find_element_by_name("urlForm")
    _urlForm.submit()

    _result = _driver.find_element_by_class_name('labeltitleresult')
    _status = _result.text
    _driver.close()
    return _status


def parseArguments():

    _parser = argparse.ArgumentParser(
            description="A quick script to check URLs against Trend Micro's Global Site Safety utility."
    )
    _parser.add_argument(
        "-f", "--file", 
        dest="file", 
        help="A file containing a list of URLs to test.  One URL per line."
    )
    _parser.add_argument(
        "-u", "--url", 
        dest="url",
        help="A single URL to test."
    )

    _parser.add_argument(
        "-d", "--debug", 
        dest="debug",
        action="store_true",
        help="A boolean flag that will enable debugging, allowing the user to see the interactions with the Global Site Safety utility and additional information on the execution of the script."
    )

    _args = _parser.parse_args()
    if _args.debug:
        print ("Args specified: ", _args)

    if _args.file == None and _args.url == None:
        print ("\nERROR: A URL to test must be specified via the command line or an input file.\n")
        _parser.print_help()
        sys.exit(1)
    
    return _args


def isValidResult(_result):
    _match = re.match('Safe|Untested|Dangerous|Suspicious',_result)
    return _match


def main():

    args = parseArguments()
    
    if args.url != None:
        status = checkSite(args.url,args.debug)
        if isValidResult(status):
            print ("%s: %s" % (args.url, status))

    if args.file != None:
        if not path.isfile(args.file):
            print("ERROR: File specified does not exist.")
            sys.exit(1)
        list = open(args.file,"r")
        for url in list:
            url = url.rstrip()
            status = checkSite(url,args.debug)
            if isValidResult(status):
                print ("%s: %s" % (url, status))


        
if __name__ == "__main__":
    main()

