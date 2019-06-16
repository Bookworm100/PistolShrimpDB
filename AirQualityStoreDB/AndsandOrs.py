from itertools import groupby
import SharedFunctions
import json
import difflib

def processAndandOrs2(key, matches, dynamicDB):
    filterItems = dynamicDB

    toWrite = ""
    selectedKeys = []
    for eachKey in filterItems:
        include = False
        for orClause in matches:
            meetsAllAnds = True
            for andClause in orClause:
                if len(andClause) % 2 != 0:
                    print("THERE IS A PROBLEM WITH THE AND CLAUSE!")
                    break
                for colIndex in range(0, len(andClause), 2):
                    col = andClause[colIndex]
                    val = andClause[colIndex + 1]
                    keys = set(k.lower() for k in dynamicDB[eachKey]['data'])
                    if col.lower() not in keys \
                            or filterItems[eachKey]['isFree'] != 'false'\
                            or filterItems[eachKey]['data'][col].lower() != val.lower():
                                meetsAllAnds = False
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
    #    for each in selectedKeys:
    #        toWrite += each + ": " + json.dumps(dynamicDB[each]['data']) + '\n'
    #    toWrite += str(len(selectedKeys)) + " items found.\n"
    return selectedKeys


def findInPattern(findInKeys, findInVals, filterItems, cols, patterns, item1, toFind=False, limit=0.8):
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
    return False


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

def searchList(cols, patterns, item1, findInKeys, findInVals, filterItems, toFind=False, limit=0.8):
    #selected = []
    foundInAPass = True
    for colIndex in range(len(cols)):
        col = ''
        # If there is a column name associated
        # with the search filer, then we
        # extract that value.
        if cols:
            col = cols[colIndex]
        val = patterns[colIndex]
        # We filter each row from the
        # filtered key value store.
        #for item1 in selectKeys:
        # We examine if a pattern is in a key if necessary.
        if findInKeys:
            ratioDistance = 0
            if toFind:
                ratioDistance = difflib.SequenceMatcher(None, item1,
                                                        val).ratio()
            predicate = (item1.find(val) != -1) or (toFind and
                                                    ratioDistance > limit)
            if predicate:
                continue
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
                    # ratioDistance = float((editDistance(item2, col))) / \
                    # float(len(item2))
                    # print("computed")
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
                        findOnce = True
            if not findOnce:
                foundInAPass = False
    return foundInAPass


def processAndandOrs(findInKeys, findInVals, matches, usage, dynamicDB, findBoth, toFind=False, limit=0.8):
    filterItems = dynamicDB

    toWrite = ""
    selectedKeys = []
    for eachKey in filterItems:
        include = False
        for orClause in matches:
            meetsAllAnds = True
            for andClause in orClause:
                if findBoth:
                    if andClause[0].find('=') != -1:
                        lineList = andClause.split('=')
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
                        meetsAllAnds = searchList(cols, patterns, eachKey,
                                          findInKeys, findInVals, filterItems, toFind=False, limit=0.8)
                else:
                    meetsAllAnds = searchList([], andClause, eachKey,
                                              findInKeys, findInVals, filterItems, toFind=False, limit=0.8)
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