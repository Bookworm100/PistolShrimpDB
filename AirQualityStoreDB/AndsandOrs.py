from itertools import groupby
import SharedFunctions
import json
import difflib


def selectKeyswithAndOrs(matches, dynamicDB):
    """ selectKeyswithAndOrs collects keys for deletes and selects.

        For every key in the key value store, each associated column
        type and value is verified alongside the required pairs.
        If, for each required pair, there exists a pair (column type and
        value) which is exactly that required pair, then that key
        is included in the list of returned keys.

        Keyword arguments:
        matches -- the list of pairs used to filter the key value store
        dynamicDB -- the key value store

        Return values:
        selectedKeys -- the list of keys selected from the store which contain
                        the pairs
    """

    filterItems = dynamicDB
    selectedKeys = []
    # We iterate through each element of
    # the key value store exactly once,
    # and include it if it meets the necessary
    # criteria: matching at least one of the
    # or clauses, and all of the inner and
    # clauses.
    for eachKey in filterItems:
        # include indicates whether or not
        # at least one of the inner and clauses
        # meets the criteria.
        include = False
        for orClause in matches:
            meetsAllAnds = True
            # Because of Delete's and Select's usages,
            # we know that columns and their values must
            # be present in pairs.
            for andClause in orClause:
                meetsAllAnds = meetsAllAnds & \
                               SharedFunctions.doesColumnTypeValueMatch(eachKey, andClause,
                                                        filterItems)
            # Once we know each pair matches, we know to
            # include them.
            if meetsAllAnds:
                include = True
        # We do not need extra checks for ors because
        # they are the union of satisfying keys,
        # and we will not have overlap because we
        # only look at each key once.
        if include:
            selectedKeys.append(eachKey)
    if len(selectedKeys) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "column types.")
    return selectedKeys


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
    #foundInAPass = True
    # If there is a column name associated
    # with the search filer, then we
    # extract that value.
    # We filter each row from the
    # filtered key value store.
    # We examine if a pattern is in a key if necessary.
    predicate1 = False
    predicate2 = False
    checkedThisColumn = predicate2
    predicate3 = False
    if findInKeys:
        ratioDistance = 0
        if toFind:
            ratioDistance = difflib.SequenceMatcher(None, item1,
                                                        pattern).ratio()
        predicate1 = (item1.find(pattern) != -1) or (toFind and
                                                    ratioDistance > limit)
    # We examine if a pattern is in a key if necessary.
    # If a column is associated with the pattern,
    # then we check only if the associated pattern
    # matches the value at that column.
    if findInVals:
        findOnce = False
        for item2 in filterItems[item1]['data']:
            if item2 is None:
                continue
            ratioDistance = 0
            if toFind and col != '':
                ratioDistance = difflib.SequenceMatcher(None, item2,
                                                            col).ratio()
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
                predicate3 = (item3.find(pattern) != -1) or (toFind and
                                                            ratioDistance > limit)\
                             or predicate3
    #    if not findOnce:
    #        foundInAPass = False
    return predicate1 or (checkedThisColumn and predicate3)


def processAndandOrs(findInKeys, findInVals, matches, usage, dynamicDB,
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
                              " As a reminder, "
                              "the usage is below: \n ", usage)
                        return ''
                    else:
                        col = lineList[0]
                        pattern = lineList[1]
                        meetsAllAnds = searchList(col, pattern, eachKey,
                                          findInKeys, findInVals, filterItems,
                                                  toFind, limit) & meetsAllAnds
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
    #else:
    #    return selectedKeys
        # We print each row that we selected.
    for each in selectedKeys:
        toWrite += each + ": " + json.dumps(dynamicDB[each]['data']) + '\n'
    toWrite += str(len(selectedKeys)) + " items found.\n"
    return toWrite

"""def findInPattern(findInKeys, findInVals, filterItems, cols, patterns, item1, toFind=False, limit=0.8):
    for colIndex in range(0, len(patterns)):
        col = ''
        # If there is a column name associated
        # with the search filer, then we
        # extract that value.
        if cols:
            col = cols[colIndex]
        val = patterns[colIndex]
        # We examine if a pattern is in a key if necessary.
        if findInKeys:
            ratioDistance = 0
            if toFind:
                ratioDistance = difflib.SequenceMatcher(None, item1,
                                                            val).ratio()
            predicate = (item1.find(val) != -1) or (toFind and
                                                        ratioDistance > limit)
            if predicate:
                return True
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
                predicate = (item2.find(col) != -1) or (toFind and
                                                            ratioDistance > limit)
                if col == '' or predicate:
                    item3 = filterItems[item1]['data'][item2]
                    if item3 is None:
                        continue
                    if toFind:
                        ratioDistance = difflib.SequenceMatcher(None, item3,
                                                                    val).ratio()
                            # ratioDistance = float((editDistance(item3, val))) / \
                            #                float(len(item3))
                            # print("computed2")
                    predicate = (item3.find(val) != -1) or (toFind and
                                                                ratioDistance > limit)
                        # print(item3)

                    if predicate:
                        return True
    return False"""


"""def processAndandOrs(findInKeys, findInVals, matches, usage, dynamicDB, findBoth, toFind=False, limit=0.8):
    # Since identification was only specified by
    # rows, we need to filter the rows by each column specified.

    # Since identification was only specified by
    # rows, we need to filter the rows by each column specified.
    filterItems = dynamicDB
    toWrite = ""
    # print(len(matches))
    # print(matches)
    # matches = matches[0]
    #print(matches)
    result = []
    print(matches)
    for orClauses in matches:
        setOfKeys = set()
        for andClause in orClauses:
            print("orclauses", orClauses)
            print("andclauses", andClause)
            line = andClause
            if findBoth:
                if line[0].find('=') != -1:
                    lineList = line.split('=')
                else:
                    lineList = andClause
                if len(lineList) % 2 != 0:
                    print("Column types must be associated with column values!"
                          " As a reminder, "
                          "the usage is below: \n ", usage)
                    error = True
                    break
                else:
                    cols = lineList[0::2]
                    patterns = lineList[1::2]
                    if len(setOfKeys) == 0:
                        setOfKeys = printSearchResult(findInKeys, findInVals, cols, patterns, filterItems, dynamicDB, toFind=False, limit=0.8)
                    else:
                        setOfKeys = setOfKeys.intersection(
                        printSearchResult(findInKeys, findInVals, cols, patterns, filterItems, dynamicDB, toFind=False, limit=0.8))
                    # print(printSearchResult(findInKeys, findInVals, cols, patterns, filterItems, toFind=False, limit=0.8))
            else:
                if len(setOfKeys) == 0:
                    setOfKeys = printSearchResult(findInKeys, findInVals, '', line, filterItems, dynamicDB,
                                                  toFind=False, limit=0.8)
                else:
                    setOfKeys = setOfKeys.intersection(
                    printSearchResult(findInKeys, findInVals, '', line, filterItems, dynamicDB, toFind=False, limit=0.8))
                # print(printSearchResult(findInKeys, findInVals, '', line, filterItems, toFind=False, limit=0.8))
        result.append(setOfKeys)
    print(len(result))
    setOfKeys = result[0]
    print(setOfKeys)
    for i in range(1, len(result)):
        print("wkjkej")
        setOfKeys = setOfKeys | result[i]
    print(len(setOfKeys))
    filterItems = list(setOfKeys)
    if len(filterItems) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "column types.")
    else:
        # We print each row that we selected.
        for each in filterItems:
            toWrite += each + ": " + json.dumps(dynamicDB[each]['data']) + '\n'
        toWrite += str(len(filterItems)) + " items found.\n"
    return toWrite
"""

"""filterItems = dynamicDB
    toWrite = ""

    selectedKeys = []

    for each in filterItems:
        satisfy = False
        for orClause in matches:
            include = True
            for andClause in orClause:
                line = andClause
                if line[0].find('=') != -1:
                    lineList = line.split('=')
                    if len(lineList) % 2 != 0:
                        print("Column types must be associated with column values!"
                              " As a reminder, "
                              "the usage is below: \n ", usage)
                        error = True
                        break
                    else:
                        cols = lineList[0::2]
                        patterns = lineList[1::2]
                    result = findInPattern(findInKeys, findInVals,
                                           filterItems, cols, patterns,
                                           each, toFind=False, limit=0.8)
                else:
                    result = findInPattern(findInKeys, findInVals, filterItems, '',
                                  line, each, toFind=False, limit=0.8)
                if result:
                    selectedKeys.append(each)
    if len(selectedKeys) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "column types.")
    else:
        # We print each row that we selected.
        for each in selectedKeys:
            toWrite += each + ": " + json.dumps(dynamicDB[each]['data']) + '\n'
        toWrite += str(len(selectedKeys)) + " items found.\n"
    return toWrite"""




""" printSearchResult filters per pattern. For each pattern specified,"""
""" each row is examined if the pattern is found in a key (if specified) or """
""" values (again, if specified). The filtered items are printed. """
""" @:param: findInKeys, whether to look through the keys """
""" @:param: findInVals, whether to look through the values """
""" @:param: cols, the column types to search through """
""" @:param: patterns, the values to look through """
""" @:return: toWrite, the string that will be written to the file """
"""def printSearchResult(findInKeys, findInVals, cols, patterns, selectKeys, dynamicDB, toFind=False, limit=0.8):
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
"""