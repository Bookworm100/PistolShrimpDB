import re
import json
from itertools import groupby
from jsonpath_ng import jsonpath, parse
import operator
import SharedFunctions
import AndsandOrs

""" This should handle anything """
""" with selects. Either completed or very, very close to completion. """
""" So far, The trivial selects are 1. SELECT * or SELECT * FROM KEYS, """
""" which writes keys to a file. All this involves is looping through """
""" the key value store dictionary in the running program and printing """
""" every key to a text file (printing directly to terminal might be a """
""" little problematic as there is a lot of data). """
""" 2. SELECT * FROM VALUES, which prints just all values to a text file. """
""" This involves looping through the key-value store stored in the """
""" dictionary and writing all values to a text file. """
""" 3. SELECT * FROM ALL which prints all values to a text file. This """
""" involves looping through the key-value dictionary and printing all """
""" the keys and all their corresponding values."""
""" 4. SELECT [key] or SELECT [key] FROM ALL involves """
""" printing the value corresponding to a given key to the console. All """
""" this involves is first inquring if the key is in the dictionary, and """
""" then if it is, then printing out its corresponding value."""
""" 5. SELECT WHERE col=tag, col2=tag2, etc. The printing is done in """
""" printSelectsSearches, but the information to be written is determined in this """
""" function, as is the default file name to be printed, which is passed to """
""" printSelectsSearches. """
""" @:param: matches, a list of strings of words """
""" @:param: dynamicDB, the key value store maintained in the program """
""" @:return: None """
def handleSelects(matches, dynamicDB):
    equalMatches = matches
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"]+', re.IGNORECASE)
    matches = parser.findall(" ".join(matches))
    toWrite = ''
    new_input = ''
    usage = "SELECT * \n SELECT * FROM KEYS \n SELECT * FROM VALUES \n" +\
            "SELECT * FROM ALL \n SELECT [key] SELECT [key] FROM ALL \n" +\
            "SELECT WHERE (col=val, col2=val2,...)"
    error = False
    if matches[1] == '*':
        if len(matches) == 2 or (len(matches) == 4 and
                                 matches[2].lower() == 'from' and
                                 matches[3].lower() == 'keys'):
            # This is the SELECT * FROM all keys
            new_input = 'allKeys.txt'
            for item in dynamicDB:
                if dynamicDB[item]['isFree'] == 'false':
                    toWrite += json.dumps(item) + '\n'
        elif len(matches) == 4 and (matches[2].lower() == 'from' and
                                    matches[3].lower() == 'values'):
            new_input = 'allValues.txt'
            for item in dynamicDB:
                if dynamicDB[item]['isFree'] == 'false':
                    toWrite += json.dumps(dynamicDB[item]['data']) + '\n'
        elif len(matches) == 4 and (matches[2].lower() == 'from' and
                                    matches[3].lower() == 'all'):
            new_input = 'allKeysValues.txt'
            for item in dynamicDB:
                if dynamicDB[item]['isFree'] == 'false':
                    toWrite += '{' + json.dumps(item) + ': ' + \
                              json.dumps(dynamicDB[item]['data']) + '}' + '\n'
        else:
            error = True
    elif (len(matches) == 2) or (len(matches) == 4 and
                                 matches[2].lower() == 'from' and
                                 matches[3].lower() == 'all'):
        if matches[1].lower() in dynamicDB and dynamicDB[matches[1].lower()]\
                    ['isFree'] == 'false':
            print(dynamicDB[matches[1].lower()]['data'], '\n')
        else:
            copy = {'data' : dynamicDB}
            some_str = "data.." + matches[1]
            #print(some_str)
            expr = parse(some_str)
            vals = set()
            for match in expr.find(copy):
                vals.add(str(match.value))
            toWrite += str(list(vals))
            new_input = 'trivials.txt'
            if toWrite == '':
                print("The key or column key is not in the store!")
    elif matches[1].lower() == 'where' and len(matches) >= 4:
        listOfKeys = []
        if "and" in " ".join(matches).lower() or "or" in " ".join(matches).lower():
            matches = SharedFunctions.conjMatches(2, equalMatches)
            listOfKeys += AndsandOrs.selectKeyswithAndOrs(matches, dynamicDB)
        else:
            matches = SharedFunctions.spaceMatches(2, equalMatches)
            listOfKeys += SharedFunctions.findMatchingKeys('', matches, dynamicDB)
        new_input = 'matches.txt'
        for each in listOfKeys:
            toWrite += json.dumps(each) + ": " + \
                       json.dumps(dynamicDB[each]['data']) + '\n'

    else:
        error = True
    if toWrite != '':
        SharedFunctions.printSelectsSearches(new_input, toWrite)
    if error:
        print("Either your format is invalid or something is "
              "not quite implemented! \n")
        print(usage)
