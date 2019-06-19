import difflib
import SharedFunctions
import json


def searchList(col, pattern, item1, findInKeys, findInVals,
               filterItems, toFind=False, limit=0.8):
    """ searchList collects keys for deletes and selects.

            Keyword arguments:
            matches -- the list of pairs used to filter the key value store
            dynamicDB -- the key value store

            Return values:
            selectedKeys -- the list of keys selected from the store which
                            contain the pairs
    """
    predicate1 = False
    predicate2 = False
    checkedThisColumn = predicate2
    predicate3 = False
    # If the user specifies to look at the keys, we compute the ratio distance
    # only if the user specified to find rather than to search.
    if findInKeys:
        ratioDistance = 0
        if toFind:
            ratioDistance = difflib.SequenceMatcher(None, item1, pattern).ratio()
        predicate1 = (item1.find(pattern) != -1) or (toFind and
                                                     ratioDistance > limit)
    # We examine if a pattern is in a key if necessary. If a column is
    # associated with the pattern, then we check only if the associated pattern
    # matches the value at that column.
    if findInVals:
        for item2 in filterItems[item1]['data']:
            if item2 is None:
                continue
            ratioDistance = 0
            if toFind and col != '':
                ratioDistance = difflib.SequenceMatcher(None, item2, col).ratio()
            predicate2 = (item2.find(col) != -1) or (toFind and
                                                     ratioDistance > limit)
            checkedThisColumn = predicate2 or checkedThisColumn
            if col == '' or predicate2:
                item3 = filterItems[item1]['data'][item2]
                if item3 is None:
                    continue
                if toFind:
                    ratioDistance = difflib.SequenceMatcher(None, item3,
                                                            pattern).ratio()
                predicate3 = (item3.find(pattern) != -1) or \
                             (toFind and ratioDistance > limit) or predicate3
    # Either the value should be found in the key, or in a
    # value matching a column (if specified).
    return predicate1 or (checkedThisColumn and predicate3)


def searchFilter(findInKeys, findInVals, matches, usage, dynamicDB,
                     checkColTypeVal, toFind=False, limit=0.8):
    filterItems = dynamicDB
    toWrite = ""
    selectedKeys = []
    for eachKey in filterItems:
        include = False
        for orClause in matches:
            meetsAllAnds = True
            for andClause in orClause:
                if checkColTypeVal:
                    if andClause[0].find('=') != -1:
                        lineList = andClause.split('=')
                    else:
                        lineList = andClause
                    if len(lineList) % 2 != 0:
                        print("Column types must be associated with column values!"
                              " As a reminder, the usage is below: \n ", usage)
                        return ''
                    else:
                        col = lineList[0]
                        pattern = lineList[1]
                        meetsAllAnds = searchList(col, pattern, eachKey,
                                                  findInKeys, findInVals,
                                                  filterItems, toFind, limit)\
                                                  & meetsAllAnds
                else:
                    meetsAllAnds = searchList('', andClause[0], eachKey,
                                              findInKeys, findInVals,
                                              filterItems, toFind, limit) \
                                              & meetsAllAnds
            if meetsAllAnds:
                include = True
        if include:
            selectedKeys.append(eachKey)
    if len(selectedKeys) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "column types.")
    for each in selectedKeys:
        toWrite += each + ": " + json.dumps(dynamicDB[each]['data']) + '\n'
    toWrite += str(len(selectedKeys)) + " items found.\n"
    return toWrite


""" There are 4 options for handling searches. These are of the form: """
""" 1. VALUES(col=tag, col2=tag2, col3=tag3….), """
""" 2. VALUES(pattern1, pattern2, pattern3), """
""" 3. KEY AND VALUES(pattern1, pattern2, pattern3), """
""" and 4. KEY (pattern1, pattern2,…) with searches. """
""" If the input does not match any format, then """
""" a message with the USAGE and the invalid format """
""" is printed out. Depending on the format used, """
""" printSearchResult is called with four arguments: """
""" whether the user is specifying to search in keys, """
""" whether the user is specifying to search in values, """
""" a list of the column tags the user wants to search in """
"""(only non empty in option 1), and a list of """
""" the patterns to be matched on. """
""" @:param: matches, a list of strings of words """
""" @:param: dynamicDB, the key value store maintained in the program """
""" @:return: None """
def handleSearches(matches, dynamicDB, isFind=False):
    # 1. VALUES(col=tag, col2=tag2, col3=tag3….)
    # 2. VALUES(pattern1, pattern2, pattern3)
    # 3. KEY AND VALUES(pattern1, pattern2, pattern3)
    # 4. KEY (pattern1, pattern2,…)
    # Cases 1 and 2
    matches = matches[1:]
    usage = "Usage: SEARCH [key] (pattern1, pattern2,…) \n \
            SEARCH VALUES (col1=pattern1, col2=pattern2, col3=pattern3….) \n \
            SEARCH VALUES (pattern1, pattern2, pattern3) \n \
            SEARCH KEY AND VALUES (pattern1, pattern2, pattern3) \ "
    findUsage = "Usage: FIND [opt:ratio] (pattern1, pattern2,…) \n \
                FIND [opt:ratio] VALUES (col1=pattern1, col2=pattern2, col3=pattern3….) \n \
                FIND [opt:ratio] VALUES (pattern1, pattern2, pattern3) \n \
                FIND [opt:ratio] KEY AND VALUES (pattern1, pattern2, pattern3) \ "
    error = False
    toWrite = ''
    limit = 0.8
    substringToCheck = " ".join(matches).lower()
    seeColTypeValue = '=' in substringToCheck
    if isFind:
        try:
            limit = float(matches[0].lower())
            matches = matches[1:]
        except:
            limit = 0.8
    if matches[0].lower() == "values":
        # Collect column names if necessary
        matches = matches[1:]
        if len(matches) == 0:
            print("Invalid format!"
                  "You need patterns! As a reminder, "
                  "the usage is below: \n ",
                  usage)
            error = True
        # If columns are called with patterns, then we separate the matches
        # out to their corresponding lists to be called in printSearchResult.
        if "and" in substringToCheck or "or" in substringToCheck:
            matches = SharedFunctions.conjMatches(0, matches)
            toWrite += searchFilter(False, True, matches,
                                                   usage, dynamicDB,
                                                   seeColTypeValue, isFind,
                                                   limit)
        else:
            newList = []
            matches = SharedFunctions.spaceMatches(0, matches)
            if seeColTypeValue:
                if len(matches) % 2 != 0:
                    print("Cols must be associated with values!")
                    print(usage)
                    error = True
                for i in range(0, len(matches), 2):
                    newList.append(list([matches[i], matches[i+1]]))
            else:
                newList = [[i] for i in matches]
            if not error:
                toWrite += searchFilter(False, True, [newList],
                                                       usage, dynamicDB,
                                                       seeColTypeValue, isFind,
                                                       limit)
            #(findInKeys, findInVals, filterItems, cols, patterns, item1, toFind=False, limit=0.8)
            #listOfKeys += SharedFunctions.findMatchingKeys('', matches, dynamicDB)


    # Case 3 (we are looking through keys and values, and the patterns are
    # are matches that are not key words specified in the clause)
    elif matches[0].lower() == "key" and matches[1].lower() == "and" and\
            matches[2].lower() == "values":
        if "and" in substringToCheck[15:] or "or" in substringToCheck:
            matches = SharedFunctions.conjMatches(3, matches)
        else:
            matches = SharedFunctions.spaceMatches(3, matches)
            matches = [[[i] for i in matches]]
        #compList = list((list(g) for k, g in groupby(matches[3:], key=lambda x: (x.lower() != 'or')) if k))
        #for i in range(0, len((compList))):
        #    item = list((list(g) for k, g in groupby(compList[i], key=lambda x: (x.lower() != 'and')) if k))
        #    compList[i] = item
        toWrite += searchFilter(True, True, matches, usage,
                                               dynamicDB, seeColTypeValue,
                                               isFind, limit)
    # Case 4 (we are looking through keys, and the patterns are
    # are matches that are not key words specified in the clause)
    elif matches[0].lower() == "key":
        #compList = list((list(g) for k, g in groupby(matches[1:], key=lambda x: (x.lower() != 'or')) if k))
        #for i in range(0, len((compList))):
        #    item = list((list(g) for k, g in groupby(compList[i], key=lambda x: (x.lower() != 'and')) if k))
        #    compList[i] = item
        if "and" in substringToCheck or "or" in substringToCheck:
            matches = SharedFunctions.conjMatches(1, matches)
        else:
            matches = SharedFunctions.spaceMatches(1, matches)
            matches = [[[i] for i in matches]]
        toWrite += searchFilter(True, False, matches, usage,
                                               dynamicDB, seeColTypeValue,
                                               isFind, limit)
    else:
        if isFind:
            print("Invalid format! Either your key is not in the store,"
                  "or you are following incorrect format. As a reminder, "
                  "the usage is below: \n ", findUsage)
        else:
            print("Invalid format! Either your key is not in the store,"
                  "or you are following incorrect format. As a reminder, "
                  "the usage is below: \n ", usage)
        error = True
    if not error and toWrite != '':
        SharedFunctions.printSelectsSearches("searchResult.txt", toWrite)
