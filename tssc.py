#!/bin/env python3

import re
import sys
import time
import argparse
from os import path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

##
## checkSite(_site,_driver)
##
## Arguments:
##      _state:     string      A url to test for "safety"
##      _driver:    webdriver   A webdriver object to use to load and interact with the page
##
## Returns:
##      _rating:    string      Safety status of site as reported by Trend Micro 
##
## Overview:
##      The checkSite subroutine uses the selenium webdriver to check the safety rating of
##      a site using Trend Micro's Global Site Safety Utility.  The safety rating is returned
##      by the subroutine.
##
def checkSite (_site,_driver):
    
    # Open the Global Site Safety page
    _driver.get('https://global.sitesafety.trendmicro.com/index.php')
    
    # The title should contain "Site Safety"
    assert "Site Safety" in _driver.title
    
    # Locate the urlname text box and clear out any contents
    _urlname = _driver.find_element_by_name("urlname")
    _urlname.clear()

    # Enter the specified URL and submit the form
    _urlname.send_keys(_site)
    _urlForm = _driver.find_element_by_name("urlForm")
    _urlForm.submit()

    # Locate the safety rating and save the text result 
    _result = _driver.find_element_by_class_name('labeltitleresult')
    _rating = _result.text

    # Return the safety rating
    return _rating


##
## getDriver(_debug)
##
## Arguments:
##      _debug:     bool        A True or False value designating if debugging should be enabled      
##
## Returns:
##      _driver:    webdriver   A selenium Firefox webdriver object 
##
## Overview:
##      The getDriver creates a Firefox webdriver object and sets a few options useful for this 
##      script.
##
def getDriver(_debug):

    # Create an options object and enable headless mode by default
    _options = Options()
    _options.headless = True

    # Disable the headless mode if debugging is enabled
    if _debug:
        _options.headless = False
    
    # Create the webdriver object
    _driver = webdriver.Firefox(options=_options)

    # Tell the webdriver to retry locating items for up to 20 seconds
    _driver.implicitly_wait(20)

    # Return the webdriver object
    return _driver


##
## parseArguments()
##
## Arguments:
##      <none>
##
## Returns:
##      _args:    argparse.Namespace    A Namespace object containing parsed arguments
##
## Overview:
##      The parseArguments subroutine creates an argparser object and parses any arguments 
##      specified.  The parsed arguments are then returned.
##
def parseArguments():

    # Create an argparser and set a description for this script
    _parser = argparse.ArgumentParser(
            description="A quick script to check URLs against Trend Micro's Global Site Safety utility."
    )

    # Define the file argument.  This will allow the testing of a list of URLs
    _parser.add_argument(
        "-f", "--file", 
        dest="file", 
        help="A file containing a list of URLs to test.  One URL per line."
    )

    # Define the URL argument.  This be used to test a single URL
    _parser.add_argument(
        "-u", "--url", 
        dest="url",
        help="A single URL to test."
    )

    # Define the debug argument.  Specifying the argument will set it to True and will enable debugging
    _parser.add_argument(
        "-d", "--debug", 
        dest="debug",
        action="store_true",
        help="A boolean flag that will enable debugging, allowing the user to see the interactions with the Global Site Safety utility and additional information on the execution of the script."
    )

    # Parse the arguments
    _args = _parser.parse_args()

    # Print the parsed arguments if debugging is enabled
    if _args.debug:
        print ("Args specified: ", _args)

    # Verify that at least one option was chosen.  Otherwise, why run this script?
    if _args.file == None and _args.url == None:
        print ("\nERROR: A URL to test must be specified via the command line or an input file.\n")
        _parser.print_help()
        sys.exit(1)
    
    # Return the parsed agruments
    return _args


##
## isValidRating(_rating)
##
## Arguments:
##      _rating:    string      The rating returned by the Global Site Safety utility
##
## Returns:
##      _match:     bool        True/False, does the rating match what is expected 
##
## Overview:
##      As of the time of writing this, there are only 4 possible ratings for a site.
##      This subroutine verifies that what was located matches one of those 4.  True is
##      returned if it does.  Otherwise, False is returned
##
def isValidResult(_rating):

    # Test the rating against current 4 options
    _match = re.match('Safe|Untested|Dangerous|Suspicious',_rating)

    # Return the results of the regex test
    return _match


##
## main()
##
## Arguments:
##      <none>
##
## Returns:
##      <none>
##
## Overview:
##      This is where all the magic happens.  Arguments are parsed, site(s) is/are tested,
##      results are verified and printed to the user, the worls id good.
##
def main():

    # Obtain the arguments specified
    args = parseArguments()

    # Create a webdriver object
    driver = getDriver(args.debug)

    # If a url was specified, test it
    if args.url != None:
        rating = checkSite(args.url,driver)
        # Print the result if it matches what we are expecting
        if isValidRating(rating):
            print ("%s: %s" % (args.url, rating))

    # Process the specified file, if one was specified
    if args.file != None:
        # Sleep for 60 seconds if a URL was already specified
        ## NOTE: Remoing this will probably result in captcha verification
        if args.url != None:
            time.sleep(60)
        # Verify the file exists, exit with an error if it doesn't
        if not path.isfile(args.file):
            print("ERROR: File specified does not exist.")
            sys.exit(1)
        # Open the specified file and loop through it
        list = open(args.file,"r")
        for url in list:
            # Remove any trailing space
            url = url.rstrip()
            # Get the site rating
            rating = checkSite(url,driver)
            # Print the result if it matches what we are expecting
            if isValidRating(rating):
                print ("%s: %s" % (url, rating))
            # Sleep for 60 seconds in between tests
            ## NOTE: Remoing this will probably result in captcha verification
            time.sleep(60)

    # Don't forget to clean up. No one wants 40,000 Firefox processes running
    driver.close()


# Send me to main
if __name__ == "__main__":
    main()

