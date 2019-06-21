import re
import json
from jsonpath_ng import parse
import SharedFunctions

""" Module: Select 
    Description: Select.py contains functions specifically 
                 to handle Select commands

    Functions: 

        handleSelects - Handles all input, including input processing,
                        relating Selects, and passes the appropriate arguments 
                        to SharedFunctions.findMatchingKeys if necessary
"""


def handleSelects(matches, dynamicDB):
    """ handleSelects handles input processing and execution of select
        statements.

    This should handle anything
    with selects. Either completed or very, very close to completion.
    So far, The trivial selects are 1. SELECT * or SELECT * FROM KEYS,
    which writes keys to a file. All this involves is looping through
    the key value store dictionary in the running program and printing
    every key to a text file (printing directly to terminal might be a
    little problematic as there is a lot of data).
    2. SELECT * FROM VALUES, which prints just all values to a text file.
    This involves looping through the key-value store stored in the
    dictionary and writing all values to a text file.
    3. SELECT * FROM ALL which prints all values to a text file. This
    involves looping through the key-value dictionary and printing all
    the keys and all their corresponding values.
    4. SELECT [key] or SELECT [key] FROM ALL involves
    printing the value corresponding to a given key to the console. All
    this involves is first inquiring if the key is in the dictionary, and
    then if it is, then printing out its corresponding value.
    5. SELECT WHERE col=tag, col2=tag2, etc. The printing is done in
    SharedFunctions.printSelectsSearches, but the information to be written
    is determined in this
    function, as is the default file name to be printed, which is passed to
    printSelectsSearches.
    6. SELECT WHERE col=tag AND/OR col2=tag2 AND/OR etc. The printing is done in
    SharedFunctions.printSelectsSearches, but the information to be written
    is determined in this
    function, as is the default file name to be printed, which is passed to
    printSelectsSearches.
    7. SELECT [anyKey] or SELECT [anyKey] FROM ALL. This examines each row
    in the key value stores and prints every value associated with the key
    provided.

    Keyword arguments:
    matches -- a list of strings of words
    dynamicDB -- the key value store maintained in the program

    No return values
    """

    equalMatches = matches
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"]+', re.IGNORECASE)
    matches = parser.findall(" ".join(matches))
    toWrite = ''
    new_input = ''
    usage = "SELECT * \n SELECT * FROM KEYS \n SELECT * FROM VALUES \n" +\
            "SELECT * FROM ALL \n SELECT [key] \n SELECT [key] FROM ALL \n" +\
            "SELECT WHERE (col=val, col2=val2,...) \n " \
            "SELECT WHERE (col=val AND/OR col2=val2 AND/OR...) \n" \
            "SELECT [anyKey] \n SELECT [anyKey] FROM ALL"
    error = False
    if matches[1] == '*':
        allKeys = len(matches) == 2 or (len(matches) == 4 and
                  matches[2].lower() == 'from' and
                  matches[3].lower() == 'keys')
        allValues = len(matches) == 4 and (matches[2].lower() == 'from' and
                    matches[3].lower() == 'values')
        allKeysValues = len(matches) == 4 and (matches[2].lower() == 'from' and
                        matches[3].lower() == 'all')
        if allKeys:
            # This is the SELECT * FROM all keys
            new_input = 'allKeys.txt'
            for item in dynamicDB:
                if dynamicDB[item]['isFree'] == 'false':
                    toWrite += json.dumps(item) + '\n'
        elif allValues:
            # This is the SELECT * FROM all Values
            new_input = 'allValues.txt'
            for item in dynamicDB:
                if dynamicDB[item]['isFree'] == 'false':
                    toWrite += json.dumps(dynamicDB[item]['data']) + '\n'
        elif allKeysValues:
            # This is the SELECT * FROM ALL
            new_input = 'allKeysValues.txt'
            for item in dynamicDB:
                if dynamicDB[item]['isFree'] == 'false':
                    toWrite += '{' + json.dumps(item) + ': ' + \
                              json.dumps(dynamicDB[item]['data']) + '}' + '\n'
        else:
            error = True
    elif matches[1].lower() == 'where' and len(matches) >= 4:
        # This refers to cases 5 and 6.
        listOfKeys = []
        # Ands/ors are selected for differently, but the default is to use the
        # findMatchingKeys function
        if " and " in " ".join(matches).lower() or " or " in " ".join(matches).lower():
            matches = SharedFunctions.conjMatches(2, equalMatches)
            listOfKeys += SharedFunctions.selectKeyswithAndOrs(matches, dynamicDB)
        else:
            matches = SharedFunctions.spaceMatches(2, equalMatches)
            listOfKeys += SharedFunctions.findMatchingKeys(matches, dynamicDB)
        new_input = 'matches.txt'
        for each in listOfKeys:
            toWrite += json.dumps(each) + ": " + \
                       json.dumps(dynamicDB[each]['data']) + '\n'
    else:
        # This is specifically for selecting for a specific key
        if matches[1].lower() in dynamicDB and dynamicDB[matches[1].lower()]\
                    ['isFree'] == 'false':
            print(dynamicDB[matches[1].lower()]['data'], '\n')
        else:
            if (matches[-2].lower() == 'from' and matches[-1].lower() == 'all'):
                matches = matches[:-2]
            matches = matches[1:]
            matches = " ".join(matches)
            # This is specifically selecting for all columns or inner keys
            # in the key value store, a trivial project!
            copy = {'data': dynamicDB}
            # The parser will find any descendant of the key value store's data
            # that is a key in any row.
            # that is a key in any row.
            anElem = json.dumps(matches)
            some_str = "data.." + anElem
            expr = parse(some_str)
            vals = set()
            # Each match is added to a set, which is written to a buffer, then
            # written to a file or terminal output.
            for match in expr.find(copy):
                vals.add(str(match.value))
            if len(vals) > 0:
                toWrite += str(list(vals))
                new_input = 'trivials.txt'
            if toWrite == '':
                print("Either the key or column key is not in the store, "
                      "your format is invalid, or something is not"
                      "quite implemented!")
    # Print or write the results to the terminal or a file
    if toWrite != '':
        SharedFunctions.printSelectsSearches(new_input, toWrite)
    if error:
        print("Either your format is invalid or something is "
              "not quite implemented! \n")
        print(usage)
