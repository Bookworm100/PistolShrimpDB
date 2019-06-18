import difflib
from itertools import groupby
import AndsandOrs
import SharedFunctions




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
            toWrite += AndsandOrs.processAndandOrs(False, True, matches,
                                                   usage, dynamicDB,
                                                   seeColTypeValue, isFind,
                                                   limit)
            #listOfKeys += AndsandOrs.processAndandOrs2('', matches, dynamicDB)
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
                toWrite += AndsandOrs.processAndandOrs(False, True, [newList],
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
            #listOfKeys += AndsandOrs.processAndandOrs2('', matches, dynamicDB)
        else:
            matches = SharedFunctions.spaceMatches(3, matches)
            matches = [[[i] for i in matches]]
        #compList = list((list(g) for k, g in groupby(matches[3:], key=lambda x: (x.lower() != 'or')) if k))
        #for i in range(0, len((compList))):
        #    item = list((list(g) for k, g in groupby(compList[i], key=lambda x: (x.lower() != 'and')) if k))
        #    compList[i] = item
        toWrite += AndsandOrs.processAndandOrs(True, True, matches, usage,
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
            #listOfKeys += AndsandOrs.processAndandOrs2('', matches, dynamicDB)
        else:
            matches = SharedFunctions.spaceMatches(1, matches)
            matches = [[[i] for i in matches]]
        toWrite += AndsandOrs.processAndandOrs(True, False, matches, usage,
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


""" printSearchResult filters per pattern. For each pattern specified,"""
""" each row is examined if the pattern is found in a key (if specified) or """
""" values (again, if specified). The filtered items are printed. """
""" @:param: findInKeys, whether to look through the keys """
""" @:param: findInVals, whether to look through the values """
""" @:param: cols, the column types to search through """
""" @:param: patterns, the values to look through """
""" @:return: toWrite, the string that will be written to the file """
def printSearchResult(findInKeys, findInVals, cols, patterns, selectKeys, dynamicDB, toFind=False, limit=0.8):
    selected = set()
    filterItems = {}
    for each in selectKeys:
        newVal = {}
        newVal[each] = dynamicDB[each]
        filterItems.update(newVal)
        #filterItems.update()
    for colIndex in range(0, len(patterns)):
        col = ''
        # If there is a column name associated
        # with the search filer, then we
        # extract that value.
        if cols:
            col = cols[colIndex]
        val = patterns[colIndex]
        # We filter each row from the
        # filtered key value store.
        for item1 in selectKeys:
            # We examine if a pattern is in a key if necessary.
            if findInKeys:
                ratioDistance = 0
                if toFind:
                    ratioDistance = difflib.SequenceMatcher(None, item1,
                                                            val).ratio()
                predicate = (item1.find(val) != -1) or (toFind and
                                                        ratioDistance > limit)
                if predicate:
                    selected.add(item1)
                    continue
            # We examine if a pattern is in a key if necessary.
            # If a column is associated with the pattern,
            # then we check only if the associated pattern
            # matches the value at that column.
            if findInVals:
                for item2 in filterItems[item1]['data']:
                    if item2 is None:
                        continue
                    ratioDistance = 0
                    if toFind and col != '':
                        ratioDistance = difflib.SequenceMatcher(None, item2,
                                                                col).ratio()
                        #ratioDistance = float((editDistance(item2, col))) / \
                                        #float(len(item2))
                        #print("computed")
                    predicate = (item2.find(col) != -1) or (toFind and
                                                            ratioDistance > limit)
                    if col == '' or predicate:
                        item3 = filterItems[item1]['data'][item2]
                        if item3 is None:
                            continue
                        if toFind:
                            ratioDistance = difflib.SequenceMatcher(None, item3,
                                                                    val).ratio()
                            #ratioDistance = float((editDistance(item3, val))) / \
                            #                float(len(item3))
                            #print("computed2")
                        predicate = (item3.find(val) != -1) or (toFind and
                                                                ratioDistance > limit)
                        #print(item3)

                        if predicate:
                            selected.add(item1)
                            #print("updated")
        return selected

