from itertools import groupby
import Main
import json
import difflib

def processAndandOrs2(key, matches, dynamicDB):
    compList = list((list(g) for k, g in groupby(matches, key=lambda x: (x.lower() != 'or')) if k))
    for i in range(0, len((compList))):
        item = list((list(g) for k, g in groupby(compList[i], key=lambda x: (x.lower() != 'and')) if k))
        compList[i] = item

    # Since identification was only specified by
    # rows, we need to filter the rows by each column specified.
    if len(compList) == 1:
        return Main.findMatchingKeys(key, compList, dynamicDB)
    filterItems = dynamicDB.keys()
    toWrite = ""
    # print(len(matches))
    # print(matches)
    # matches = matches[0]
    # print(matches)s
    selectedKeys = []
    for eachKey in filterItems:
        satisfy = False
        for orClause in compList:
            include = True
            for andClause in orClause:
                for colIndex in range(0, len(andClause), 2):
                    col = orClause[colIndex]
                    val = orClause[colIndex + 1]
                    if col in filterItems[eachKey]['data'] \
                            and filterItems[eachKey]['isFree'] == 'false':
                        if filterItems[eachKey]['data'][col] != val:
                            include = False
                    else:
                        include = False
            if include:
                satisfy = True
        if satisfy:
            selectedKeys.append(eachKey)
    if len(selectedKeys) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "column types.")
    else:
        # We print each row that we selected.
        for each in selectedKeys:
            toWrite += each + ": " + json.dumps(dynamicDB[each]['data']) + '\n'
        toWrite += str(len(filterItems)) + " items found.\n"
    return toWrite


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


def processAndandOrs(dynamicDB, findInKeys, findInVals, matches, usage, toFind=False, limit=0.8):
    # Since identification was only specified by
    # rows, we need to filter the rows by each column specified.
    filterItems = dynamicDB.keys()
    toWrite = ""
    compList = list((list(g) for k, g in groupby(matches, key=lambda x: (x.lower() != 'or')) if k))
    for i in range(0, len((compList))):
        item = list((list(g) for k, g in groupby(compList[i], key=lambda x: (x.lower() != 'and')) if k))
        compList[i] = item

    selectedKeys = []

    for each in filterItems:
        satisfy = False
        for orClause in compList:
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
    return toWrite



