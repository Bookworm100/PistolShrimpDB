import difflib
import SharedFunctions
import json

""" Module: Search 
    Description: Search.py contains functions specifically to handle Search and
                 Find input commands

    Functions: 

        searchList - For each key, col pattern and val pattern specified the
                     user, searchList examines whether these patterns are
                     substrings of corresponding column values of that key
                     (for Search) or of a ratioDistance less than the limit
                     specified of corresponding column values of that key
                     (for Find)
        
        searchFilter - Filters keys by criteria the user supplied and writes
                       their pertaining information to a buffer string used
                       by handleSearches for output
        
        handleSearches - Handles all input, including input processing,
                         relating Searches and Finds, and passes the 
                         appropriate arguments to searchFilter
"""


def searchList(col, pattern, item1, findInKeys, findInVals,
               filterItems, toFind=False, limit=0.8):
    """ searchList is a helper which designates whether to include a key in a
    key collection for deletes and selects.

    For a given user-specified column type and pattern or possible matches (in
    of find), the keys, followed by each of the values themselves are compared
    either as a substring or using a ratioDistance metric from difflib, and
    then if a match is found in the values with its type or in the keys,
    we return true.

    Keyword arguments:
    col -- the user specified column type
    pattern -- the user specified pattern
    item1 -- the key we are interested in
    findInKeys -- a Boolean if we want to examine keys
    findInVals -- a Boolean if we want to examine values
    filterItems -- the key value store
    toFind -- whether the user used a Find Command instead of search. By
              default it is false.
    limit -- the ratioDistance limit for the find option. By default, it is
             arbitrarily set to 0.8.

    Return values:
    toInclude -- a Boolean indicating whether to include the key in the list
                 of keys selected from the store which are close matches to
                 the pairs
    """

    predicate1 = False
    predicate2 = False
    checkedAColumn = predicate2
    predicate3 = False
    # If the user specifies to look at the keys, we compute the ratio distance
    # only if the user specified to find rather than to search.
    if findInKeys:
        ratioDistance = 0
        if toFind:
            ratioDistance = difflib.SequenceMatcher(None, item1, pattern).ratio()
        predicate1 = (item1.find(pattern) != -1) \
            or (toFind and ratioDistance > limit)

    # We examine if a pattern is in a key if necessary. If a column is
    # associated with the pattern, then we check only if the associated pattern
    # matches the value at that column.
    if findInVals:
        for item2 in filterItems[item1]['data']:
            if item2 is None:
                continue

            # Compute ratio distance only if the user specified to find
            # and not to search
            ratioDistance = 0
            if toFind and col != '':
                ratioDistance = difflib.SequenceMatcher(None, item2, col).ratio()

            # Figure out if the column type, if specified, is in the row or
            # if we want a ratioDistance from a column type/key in the row.
            predicate2 = (item2.find(col) != -1) \
                or (toFind and ratioDistance > limit)
            checkedAColumn = predicate2 or checkedAColumn
            # If the column exists or is within a ratio distance limit,
            # then we want to check the actual value at the row, with
            # specified column (in this case, each of the keys stored per
            # key value store entry)
            if col == '' or predicate2:
                item3 = filterItems[item1]['data'][item2]
                if item3 is None:
                    continue
                if toFind:
                    ratioDistance = difflib.\
                        SequenceMatcher(None, item3, pattern).ratio()
                # predicate3 determines if the value an exact substring (for
                # search) or within a certain ratioDistance
                predicate3 = (item3.find(pattern) != -1) or \
                             (toFind and ratioDistance > limit) or predicate3

    # Either the value should be found in the key, or in a
    # value matching a column (if specified).
    toInclude = predicate1 or (checkedAColumn and predicate3)
    return toInclude


def searchFilter(findInKeys, findInVals, matches, usage, dynamicDB,
                     checkColTypeVal, toFind=False, limit=0.8):
    """ searchFilter writes the information of keys meeting the criteria
    specified by the matches argument.

    For each key in the key value store, we extract each ored statement,
    and for each anded statement nested in the ored statement, we check
    all the criteria match using searchList, and depending on its return
    value, we include the key.

    Keyword Arguments:
    findInKeys -- a Boolean indicating whether to include searching through
                  keys
    findInVals -- a Boolean indicating whether to include searching through
                  values
    matches -- the list of criteria based on patterns alone or col/val pattern
               pairs which are either checked for substrings or ratioDistances
    usage -- The usage to display in case things go wrong, or the user made a
             mistake in supplying input
    dynamicDB -- the key value store
    checkColTypeVal -- a Boolean indicating if the input is in col/val pairs or
                       not
    toFind -- whether the user used a Find Command instead of search. By
              default it is false.
    limit -- the ratioDistance limit for the find option. By default, it is
             arbitrarily set to 0.8.

    Return values:
    toWrite -- the buffer to which selected keys' information is written
    """

    filterItems = dynamicDB
    toWrite = ""
    selectedKeys = []
    # We only examine each key/row in the key value store once.
    for eachKey in filterItems:
        # If at least one of the inner clauses is satisfied, then we use the
        # information of this key.
        include = False
        for orClause in matches:
            # If at all of the inner clauses is satisfied, then we use the
            # information of this key.
            meetsAllAnds = True
            for andClause in orClause:
                # If the matches are in pairs of column types and values,
                # then we feed in each column and pattern separately
                # and check if the key is a match with all of them,
                # which is what meetAllAnds is for.
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
                # Otherwise, we only look at each pattern individually only.
                else:
                    meetsAllAnds = searchList('', andClause[0], eachKey,
                                              findInKeys, findInVals,
                                              filterItems, toFind, limit) \
                                              & meetsAllAnds
            if meetsAllAnds:
                include = True
        # This scope is for the or Clauses, and since at least one needs to be
        # met, so we include if at least one meetAllAnds condition is met.
        if include:
            selectedKeys.append(eachKey)
    if len(selectedKeys) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "column types.")
    # We write the information of each selected key to a string, and return
    # that for writing to a file or terminal.
    for each in selectedKeys:
        toWrite += each + ": " + json.dumps(dynamicDB[each]['data']) + '\n'
    toWrite += str(len(selectedKeys)) + " items found.\n"
    return toWrite


def handleSearches(matches, dynamicDB, isFind=False):
    """ handleSearches handles all the commands relating to search and find.

    There are 8 options for handling searches and finds. These are of the form:
    1. VALUES(col=tag, col2=tag2, col3=tag3….),
    2. VALUES(pattern1, pattern2, pattern3),
    3. KEY AND VALUES(pattern1, pattern2, pattern3),
    4. KEY (pattern1, pattern2,…),
    5. VALUES(col=tag AND/OR col2=tag2 AND/OR col3=tag3….),
    6. VALUES(pattern1 AND/OR pattern2 AND/OR pattern3)
    7. KEY AND VALUES(pattern1 AND/OR pattern2 AND/OR pattern3),
    8. KEY (pattern1 AND/OR pattern2 AND/OR…),

    If the input does not match any format, then
    a message with the USAGE and the invalid format
    is printed out. Depending on the format used,
    SharedFuncions.printSelectsSearchResult is called with
    four arguments:
    whether the user is specifying to search in keys,
    whether the user is specifying to search in values,
    a list of the column tags the user wants to search in
    (only non empty in option 1), and a list of
    the patterns to be matched on.

    Keyword arguments:
    matches -- a list of strings of words
    dynamicDB -- the key value store maintained in the program
    isFind -- whether the user used a Find Command instead of search. By
              default it is false.

    No return values
    """

    # Cases 1, 2, 5, 6
    matches = matches[1:]
    usage = "Usage: SEARCH [key] (pattern1, pattern2,…) \n \
            SEARCH VALUES (col1=pattern1, col2=pattern2, col3=pattern3….) \n \
            SEARCH VALUES (pattern1, pattern2, pattern3) \n \
            SEARCH KEY AND VALUES (pattern1, pattern2, pattern3) \n \
            SEARCH VALUES(col=tag AND/OR col2=tag2 AND/OR col3=tag3….) \n \
            SEARCH VALUES(pattern1 AND/OR pattern2 AND/OR pattern3) \n \
            SEARCH KEY AND VALUES(pattern1 AND/OR pattern2 AND/OR pattern3) \n \
            SEARCH KEY (pattern1 AND/OR pattern2 AND/OR…), \ "
    findUsage = "Usage: FIND [opt:ratio] (pattern1, pattern2,…) \n \
                FIND [opt:ratio] VALUES (col1=pattern1, col2=pattern2, " \
                        "col3=pattern3….) \n \
                FIND [opt:ratio] VALUES (pattern1, pattern2, pattern3) \n \
                FIND [opt:ratio] KEY AND VALUES (pattern1, pattern2, pattern3) \n \
                FIND VALUES(col=tag AND/OR col2=tag2 AND/OR col3=tag3….) \n \
                FIND VALUES(pattern1 AND/OR pattern2 AND/OR pattern3) \n \
                FIND KEY AND VALUES(pattern1 AND/OR pattern2 AND/OR pattern3) \n \
                FIND KEY (pattern1 AND/OR pattern2 AND/OR…), \ "
    error = False
    toWrite = ''
    limit = 0.8
    substringToCheck = " ".join(matches).lower()
    seeColTypeValue = '=' in substringToCheck
    # Check if the user specified a limit since it is optional
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
        # out to their corresponding lists to be called in searchFilter
        # depending on whether the user specified commas or and/or
        if "and" in substringToCheck or "or" in substringToCheck:
            matches = SharedFunctions.conjMatches(0, matches)
            toWrite += searchFilter(False, True, matches, usage, dynamicDB,
                                    seeColTypeValue, isFind, limit)
        else:
            newList = []
            matches = SharedFunctions.spaceMatches(0, matches)
            # Check validity of other input specified
            if seeColTypeValue:
                if len(matches) % 2 != 0:
                    print("Cols must be associated with values!")
                    print(usage)
                    error = True
                # Match the list to be of an inner nested list of
                # anded arguments, as that is what the comma serves as
                for i in range(0, len(matches), 2):
                    newList.append(list([matches[i], matches[i+1]]))
            else:
                # Match the list to be of an inner nested list of
                # anded arguments, as that is what the comma serves as
                newList = [[i] for i in matches]
            if not error:
                toWrite += searchFilter(False, True, [newList], usage, dynamicDB,
                                        seeColTypeValue, isFind, limit)
    # Case 3/7 (we are looking through keys and values, and the patterns are
    # are matches that are not key words specified in the clause)
    elif matches[0].lower() == "key" and matches[1].lower() == "and" and\
            matches[2].lower() == "values":
        if "and" in substringToCheck[15:] or "or" in substringToCheck:
            matches = SharedFunctions.conjMatches(3, matches)
        else:
            matches = SharedFunctions.spaceMatches(3, matches)
            # Match the list to be of an inner nested list of
            # anded arguments, as that is what the comma serves as
            matches = [[[i] for i in matches]]
        toWrite += searchFilter(True, True, matches, usage, dynamicDB,
                                seeColTypeValue, isFind, limit)
    # Case 4/8 (we are looking through keys, and the patterns are
    # are matches that are not key words specified in the clause)
    elif matches[0].lower() == "key":
        if "and" in substringToCheck or "or" in substringToCheck:
            matches = SharedFunctions.conjMatches(1, matches)
        else:
            matches = SharedFunctions.spaceMatches(1, matches)
            # Match the list to be of an inner nested list of
            # anded arguments, as that is what the comma serves as
            matches = [[[i] for i in matches]]
        toWrite += searchFilter(True, False, matches, usage, dynamicDB,
                                seeColTypeValue, isFind, limit)
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
