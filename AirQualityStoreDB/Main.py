# Import statements:
# The documents we're using require JSON
import os.path
import json
import sys
import ast
import re
import random
import string

# Note: all global variables will not be modified
# size of blocks of memory in bytes
blockSize = 1000
# set of acceptable columns
typesSet = {'measureId', 'measureDesc', 'stateId', 'stateName', 'countyId',
            'countyName', 'year', 'measurement', 'units', 'unitSymbol'}


""" updateFileWithUpdates modifies the  """
""" value store from the storage file. As Python 3.7 preserves order """
""" in dictionaries, it's possible to recall the positions of keys (in the """
""" storage file) to be updated by """
""" using simple Python function calls (handled in the main function). """
""" The list of these indices is the argument. As the key did not change, """
""" the positions that changed are passed in as a list with its associated """
""" key and row and then using read lines, we modifiy only the lines """
""" we want and then write them back to the file. """
def updateFileWithUpdates(storageDbFile, updatedRows):
    # TODO: Change this to only read applicable lines,
    # We can write back
    # We read each line currently in the storage file
    # as a separate element in a list.
    with open(storageDbFile, 'r+b') as open_file:
        lineList = open_file.readlines()
    # We only modify the lines in the list which
    # had their values modified.
    for tup in updatedRows:
        #file.seek(c * blockSize + blockSize - sys.getsizeof(toByte))
        toWrite1 = '{' + json.dumps(tup[1]) + ': ' + \
                   json.dumps(tup[2]) + '}' + '\n'
        # We encode the key-value pair in binary and
        # write to file.
        toByte1 = toWrite1.encode('utf-8')
        toWrite2 = ('\0' * (blockSize - sys.getsizeof(toByte1)))
        toByte2 = toWrite2.encode('utf-8')
        lineList[tup[0]] = toByte2 + toByte1
    # We write the modified lines back to the file.
    with open(storageDbFile, 'w+b') as open_file:
        open_file.writelines(lineList)


""" updateFileWithDeletes removes items marked for deletion in the key """
""" value store from the storage file. As Python 3.7 preserves order """
""" in dictionaries, it's possible to recall the positions of keys (in the """
""" storage file) to be deleted by """
""" using simple Python function calls (handled in the main function). """
""" The list of these indices is the argument."""
def updateFileWithDeletes(storageDbFile, indicesDeleted):
    # TODO: We can read certain lines, so something nice would be to only read
    # lines pushed back
    # We read each line currently in the storage file
    # as a separate element in a list.
    with open(storageDbFile, 'r+b') as open_file:
        lineList = open_file.readlines()
    # We sort the indices in reverse, and remove
    # the value (and line) corresponding to each index in the
    # storage file.
    for index in sorted(indicesDeleted, reverse=True):
        del lineList[index]
    # We write the modified lines back to the file.
    with open(storageDbFile, 'w+b') as open_file:
        open_file.writelines(lineList)


""" In updateFileWithInserts, """
""" We are appending to the end of the file, as all rows to be deleted """
""" have been deleted. We write a new row corresponding to each value we """
""" insert. The format of writing should be similar to the method of first """
""" writing in the lines in the first place."""
def updateFileWithInserts(storageDbFile, insertedRows, maximumPosition):
    with open(storageDbFile, 'a+b') as file1:
        for item1 in insertedRows:
            maximumPosition += 1
            insertedRows[item1]['position'] = maximumPosition
            toWrite1 = '{' + json.dumps(item1) + ': ' + \
                       json.dumps(insertedRows[item1]) + '}' + '\n'
            # We encode the key-value pair in binary and
            # write to file.
            toByte1 = toWrite1.encode('utf-8')
            file1.write(('\0'*(blockSize-sys.getsizeof(toByte1)))
                        .encode('utf-8'))
            file1.write(toByte1)


""" printSearchResult filters per pattern. For each pattern specified,"""
""" each row is examined if the pattern is found in a key (if specified) or """
""" values (again, if specified). The filtered items are printed. """
def printSearchResult(findInKeys, findInVals, cols, patterns):
    # Since identification was only specified by
    # rows, we need to filter the rows by each column specified.
    filterItems = dynamicDB
    for colIndex in range(0, len(patterns)):
        col = ''
        # If there is a column name associated
        # with the search filer, then we
        # extract that value.
        if cols:
            col = cols[colIndex]
        val = patterns[colIndex]
        selected = {}
        # We filter each row from the
        # filtered key value store.
        for item1 in filterItems:
            # We examine if a pattern is in a key if necessary.
            if findInKeys:
                if item1.find(val) != -1:
                    newVal = {}
                    newVal[item1] = filterItems[item1]
                    selected.update(newVal)
                    continue
            # We examine if a pattern is in a key if necessary.
            # If a column is associated with the pattern,
            # then we check only if the associated pattern
            # matches the value at that column.
            if findInVals:
                for item2 in filterItems[item1]['data']:
                    if col == '' or item2.find(col) != -1:
                        if filterItems[item1]['data'][item2].find(val) != -1:
                            newVal = {}
                            newVal[item1] = filterItems[item1]
                            selected.update(newVal)
        filterItems = selected
    if len(filterItems) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "tags.")
        return
    else:
        # We print each row that we selected.
        for each in filterItems:
            print(each, ": ", dynamicDB[each]['data'], '\n')
        print(len(filterItems), " items found.\n")


""" performTempDeletion removes the values or values assicated with the key """
""" from the dictionary holding the database, and keep track of what might """
""" be removed from the storage file upon exiting or quitting. """
def performTempDeletion(key, values, dynamicDB):
    selectedKeys = []
    # If the key-value to delete is simply
    # identifiable by a key, we simply
    # mark that key for deletion.
    if len(values) == 1:
        selectedKeys.append(key)
    else:
        # Since identification was only specified by
        # rows, we need to filter the rows by each column specified
        # and mark these keys for deletion.
        filterItems = dynamicDB
        # Check that all tags/columns are matched correctly
        if len(values) % 2 == 1:
            print("Tags must be associated with column values!")
            return []
        for colIndex in range(0, len(values), 2):
            col = values[colIndex]
            val = values[colIndex + 1]
            selected = {}
            for item1 in filterItems:
                if col in filterItems[item1]['data'] \
                        and filterItems[item1]['isFree'] == 'false':
                    if filterItems[item1]['data'][col] == val:
                        newVal = {}
                        newVal[item1] = filterItems[item1]
                        selected.update(newVal)
            filterItems = selected
        if len(filterItems) == 0:
            print("Sorry, nothing in the store matches! Check your input or "
                  "tags. As a friendly reminder, the accepted columns are "
                  "measureId, measureDesc, stateId, stateName, "
                  "countyId,"
                  "countyName, year, measurement, units, unitSymbol")
            return []
        for item in filterItems:
            selectedKeys.append(item)
    return selectedKeys


""" generateNewRows will insert the new values to the dictionary key value """
""" store, and keep track of what should get added to the storage file """
""" upon exiting or quitting. """
def generateNewRows(colValList):
    # check that all columns are valid, and build up a dictionary.
    # By looping through every pair, and
    newValues = {}
    if len(colValList) % 2 == 1:
        print("Tags must be associated with column values! \n Usage:\n INSERT "
              "[key] WITH "
              "VALUES (col=tag, col2=tag2...) \n INSERT VALUES (col=tag,"
                " col2=tag2, col3=tag3...)")
        return {}
    for i in range(0, len(colValList), 2):
        if colValList[i] in typesSet:
            newValues[colValList[i]] = colValList[i+1]
        else:
            print("Invalid tag type!\n Usage:\n INSERT [key] WITH "
                  "VALUES (col=tag, col2=tag2...) \n INSERT VALUES (col=tag,"
                  " col2=tag2, col3=tag3...) \n And tags must be "
                  "one of measureId, measureDesc, stateId, stateName, "
                  "countyId,"
                  "countyName, year, measurement, units, unitSymbol")
            return {}
    return newValues


""" generateRandomKey generates a random key to be used when inserting new """
""" values to the dictionary key value store. """
def generateRandomKey():
    key = 'row-' + ''.join(random.choices(string.ascii_lowercase +
                                     string.digits, k=4))
    key = key + ''.join(random.choices('!@#$%^&~_-.+', k=1))
    key = key + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    key = key + ''.join(random.choices('!@#$%^&~_-.+', k=1))
    key = key + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return key

""" handle updates handles anything in the form UPDATE [key] WTIH VALUES """
""" (col=tag, col2=tag2, etc). Any other format causes the file to abandon """
""" the modification. Through each (col=tag, col2=tag2, etc), we change """
""" tag type's value to be the new value the user passed in. This set of """
""" changed values is then set to be the data with the value associated """
""" with the key. Other irregularities causing abandonment of modification """
""" include the type not being in the set of accepted types, and having """
""" tags/values without the other. """
def handleUpdates(matches, dynamicDB):
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+]+', re.IGNORECASE)
    matches = parser.findall(" ".join(matches))
    if matches[2].lower() == 'with' and matches[3].lower() == 'values' \
            and len(matches) >= 5:
        # check if key already exists in the key value store
        key = matches[1].lower()
        if key in dynamicDB and dynamicDB[key]['isFree'] == 'false':
            allVals = dynamicDB[key]['data']
            replaced = allVals
            matches = matches[4:]
            # Check that all tags/columns are matched correctly
            if len(matches) % 2 == 1:
               print("Tags must be associated with column values!"
                     " \n Usage:\n UPDATE "
                     "[key] WITH "
                     "VALUES (col=tag, col2=tag2...)")
               return ()
            # Check that either the column we want to modify
            # is in the row or is in the set. Otherwise,
            # this is an invalid input.
            for colIndex in range(0, len(matches), 2):
               if matches[colIndex] in allVals or\
                    matches[colIndex] in typesSet:
                   allVals[matches[colIndex]] = matches[colIndex + 1]
               else:
                   print(matches[colIndex], " is an invalid tag type!\n "
                                            "Usage:\n UPDATE [key] WITH "
                         "VALUES (col=tag, col2=tag2...) \n  And tags must be "
                         "one of measureId, measureDesc, stateId, stateName, "
                         "countyId,"
                         "countyName, year, measurement, units, unitSymbol")
                   return ()
            # Now set the data of the row to be the modified values.
            dynamicDB[key]['data'] = allVals
            return {key: {'isFree': 'false', 'data': allVals}}, \
                   {key: {'isFree': 'false', 'data': replaced}}
        else:
            print("The key is not in the store!")
    else:
        print("UPDATE format is incorrect. Usage:\n UPDATE [key] WITH "
              "VALUES (col=tag, col2=tag2...)")
        return ()


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
def handleSearches(matches, dynamicDB):
    # 1. VALUES(col=tag, col2=tag2, col3=tag3….)
    # 2. VALUES(pattern1, pattern2, pattern3)
    # 3. KEY AND VALUES(pattern1, pattern2, pattern3)
    # 4. KEY (pattern1, pattern2,…)
    # Cases 1 and 2
    matches = matches[1:]
    if matches[0].lower() == "values":
        # Collect column names if necessary
        cols = []
        patterns = []
        matches = matches[1:]
        if len(matches) == 0:
            print("Invalid format!"
                  "You need patterns! As a reminder, "
                  "the usage is below: \n "
                  "Usage: SEARCH [key] (pattern1, pattern2,…) \n \
                   SEARCH VALUES (col1=pattern1, col2=pattern2, col3=pattern3….) \n \
                   SEARCH VALUES (pattern1, pattern2, pattern3) \n \
                   SEARCH KEY AND VALUES (pattern1, pattern2, pattern3) \ ")
            return
        # If columns are called with patterns, then we separate the matches
        # out to their corresponding lists to be called in printSearchResult.
        if matches[0].find('=') != -1:
            for match in matches:
                match = match.split('=')
                if len(match) != 2:
                    print("Tags must be associated with column values!"
                          " As a reminder, "
                          "the usage is below: \n "
                          "Usage: SEARCH [key] (pattern1, pattern2,…) \n \
                   SEARCH VALUES (col1=pattern1, col2=pattern2, "
                          "col3=pattern3….) \n \
                   SEARCH VALUES (pattern1, pattern2, pattern3) \n \
                   SEARCH KEY AND VALUES (pattern1, pattern2, pattern3) \ ")
                    return
                cols.append(match[0])
                patterns.append(match[1])
        else:
            patterns = matches
        printSearchResult(False, True, cols, patterns)
    # Case 3 (we are looking through keys and values, and the patterns are
    # are matches that are not key words specified in the clause)
    elif matches[0].lower() == "key" and matches[1].lower() == "and" and\
            matches[2].lower() == "values" or matches[0] == "*":
        printSearchResult(True, True, [], matches[3:])
    # Case 4 (we are looking through keys, and the patterns are
    # are matches that are not key words specified in the clause)
    elif matches[0].lower() == "key":
        printSearchResult(True, False, [], matches[1:])
    else:
        print("Invalid format! Either your key is not in the store,"
              "or you are following incorrect format. As a reminder, "
              "the usage is below: \n "
              "Usage: SEARCH [key] (pattern1, pattern2,…) \n \
                   SEARCH VALUES (col1=pattern1, col2=pattern2, "
              "col3=pattern3….) \n \
                   SEARCH VALUES (pattern1, pattern2, pattern3) \n \
                   SEARCH KEY AND VALUES (pattern1, pattern2, pattern3) \ ")


""" This handles the printing of selects to a file or output. """
""" First, the user is prompted to indicate whether to print the """
""" output to terminal. Next, if the output is large, and the user """
""" indicates that they would like the output to be printed to the """
""" terminal, the user is notified, and is prompted whether they want to """
""" proceed with printing to terminal. In the case that they want to """
""" print to file, the user is prompted to indicate if they would like """
""" to specify a file to store the output. If not, the given default """
""" filename is used. If so, then the program attempts to open or create """
""" the file, and if an error is thrown in case the file cannot be created, """
""" then, the user is prompted to indicate if they would like to specify a """
""" file to store the output. This repeats until the user types in N, or """
""" if they specify a valid file path. In any case the user is prompted to """
""" type Y or N and they do not, they are prompted again to type Y or N. """
def printSelects(default_file, toWrite):
    written = False
    # Does the user want to print output to the terminal?
    n = input("Would you like to print the output to the terminal?"
              " Type Y or N only. \n")
    # In case of invalid output
    while n.lower() != "y" and n.lower() != "n":
        n = input("Sorry, we did not quite understand. Please type "
                  "Y only if you want to print to output or N"
                  "if you don't and want to print to a file.\n")
    # The user must confirm if the size of the output
    # is big.
    if n.lower() == "y" and sys.getsizeof(toWrite) > 2000:
        n = input("The size of the output is pretty big. "
                  "Are you sure? Again, type Y or N.\n ")
        while n.lower() != "y" and n.lower() != "n":
            n = input("Sorry, we did not quite understand. Please type "
                      "Y only if you want to print to output or N"
                      "if you don't and want to print to a file,"
                      "given that the file size is big.\n")
    # Print to terminal here.
    if n.lower() == "y":
        print(toWrite)
    else:
        # The user is prompted to indicate if they want to use a custom file.
        n = input("Would you like to create a custom file with the output?"
                  " Type Y or N only. \n")
        while not written:
            try:
                new_input = default_file
                # If the input is invalid
                while n.lower() != "y" and n.lower() != "n":
                    n = input("Sorry, we did not quite understand. Please type"
                          " Y only if you want to create a custom file or N"
                        "if you don't and want to use our custom file.\n")
                # The user types in the desired file path.
                if n.lower() == "y":
                    new_input = input("Please type in the file name, which can"
                                  " include the path if it's not being stored"
                                  " in the location of this program:\n")
                # The file is opened or created for writing.
                with open(new_input, 'w') as file:
                    file.write(toWrite)
                    written = True
            except IOError:
                # In the case the file cannot be created, the user is
                # asked if they changed their mind and want to use the
                # default file instead.
                n = input("Sorry, this path seems to be invalid."
                              " Would you still like to create a custom file? "
                              " Again, type Y or N.\n")


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
""" printSelects, but the information to be written is determined in this """
""" function, as is the default file name to be printed, which is passed to """
""" printSelects. """
def handleSelects(matches, dynamicDB):
    # return nothing
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+]+', re.IGNORECASE)
    matches = parser.findall(" ".join(matches))
    toWrite = ''
    new_input = ''
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
            print("Either your format is invalid or something is not quite"
                  " implemented! \n")
            return
    elif (len(matches) == 2) or (len(matches) == 4 and
                                 matches[2].lower() == 'from' and
                                 matches[3].lower() == 'all'):
        if matches[1].lower() in dynamicDB and dynamicDB[matches[1].lower()]\
                    ['isFree'] == 'false':
            print(dynamicDB[matches[1].lower()]['data'], '\n')
        else:
            print("The key is not in the store!")
    elif matches[1].lower() == 'where' and len(matches) >= 4:
        matches = matches[2:]
        listOfKeys = performTempDeletion('', matches, dynamicDB)
        new_input = 'matches.txt'
        for each in listOfKeys:
            toWrite += json.dumps(each) + ": " + \
                       json.dumps(dynamicDB[each]['data']) + '\n'
    else:
        print("Either your format is invalid or something is "
              "not quite implemented! \n")
        return
    if toWrite != '':
        printSelects(new_input, toWrite)


""" handleDeletes passes either a key or a set of values to the function """
""" marking keys for deletion. The matches generated using regex are used """
""" for this purpose. If a key is not in the store, then a message """
""" explaining this is printed out. If the format is incorrect (not """
""" as DELETE [key], or DELETE VALUES (col=tag, col2=tag2, col3=tag3….) """
""" a usage is printed out, and the current operation is abandoned. """
def handleDeletes(matches, dynamicDB):
    key = ''
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+]+', re.IGNORECASE)
    matches = parser.findall(" ".join(matches))
    # This is if the input is in the form DELETE VALUES (col=tag, col2=tag2...)
    if matches[1].lower() == 'values' and len(matches) >= 3:
        matches = matches[2:]
    # This is if just a key was specified.
    elif len(matches) == 2:
        if matches[1].lower() in dynamicDB and dynamicDB[matches[1].lower()]\
                    ['isFree'] == 'false':
            key = matches[1].lower()
            matches = [matches[1]]
        else:
            print("The key is not in the store!")
            return {}
    else:
        print("Delete format is incorrect. Usage:\n DELETE [key] "
              " \n DELETE VALUES (col=tag,"
              " col2=tag2, col3=tag3...)")
        return {}
    selectedKeys = performTempDeletion(key, matches, dynamicDB)
    if len(selectedKeys) > 0:
        return selectedKeys
    return []


""" handleInserts passes a set of matches generated using regex. """
""" If a key is in the store, then a message """
""" explaining this is printed out and a random key is generated instead."""
""" If the format is incorrect (not """
""" as INSERT [key] WITH VALUES (col=tag, col2=tag2, col3=tag3….), """
""" INSERT VALUES (col=tag, col2=tag2, col3=tag3…), """
""" a usage is printed out, and the current operation is abandoned. """
def handleInserts(matches, dynamicDB):
    key = ''
    values = {}
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+]+', re.IGNORECASE)
    matches = parser.findall(" ".join(matches))
    # This is if the user inputs in the format
    # INSERT [key] WITH VALUES (col=tag, col2=tag2, col3=tag3….)
    if matches[2].lower() == 'with' and matches[3].lower() == 'values' \
            and len(matches) >= 5:
        # check if key already exists in the key value store
        key = matches[1].lower()
        if key in dynamicDB and dynamicDB[key]['isFree'] == 'false':
            print("Key already in key value store. Selecting new random "
                  "key instead...\n")
            while key in dynamicDB:
                key = generateRandomKey()
        matches = matches[4:]
        # This function parses the matches and generates new rows in the
        # proper format.
        values = generateNewRows(matches)
    # This is if the user inputs in the format
    # INSERT VALUES (col=tag, col2=tag2, col3=tag3…)
    elif matches[1].lower() == 'values' and len(matches) >= 3:
        matches = matches[2:]
        while key in dynamicDB or key == '':
            key = generateRandomKey()
        values = generateNewRows(matches)
    else:
        print("Insert format is incorrect. Usage:\n INSERT [key] WITH "
              "VALUES (col=tag, col2=tag2...) \n INSERT VALUES (col=tag,"
              " col2=tag2, col3=tag3...)")
        return {}
    if values != {}:
        return {key: {'isFree': 'false', 'data': values}}


""" handleInput will be used to execute commands to change the key value """
""" store. This will soon handle insertions, deletions, select statements, """
""" update statements, and search statements. Insert commands will return """
""" the new rows, Delete statements will simply change the tag values  """
""" and return nothing, SELECT and SEARCH STATEMENTS will print the outputs """
""" while also returning nothing."""
def handleInput(command, dynamicDB):
    # check the inputs
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+=]+', re.IGNORECASE)
    matches = parser.findall(command)
    if matches[0].lower() == 'insert':
        return handleInserts(matches, dynamicDB), [], ()
    elif matches[0].lower() == 'delete':
        return {}, handleDeletes(matches, dynamicDB), ()
    elif matches[0].lower() == 'select':
        handleSelects(matches, dynamicDB)
    elif matches[0].lower() == 'search':
        handleSearches(matches, dynamicDB)
    elif matches[0].lower() == 'update':
        return {}, [], handleUpdates(matches, dynamicDB)
    return {}, [], ()

""" setUpDatabase initilizes the key value store from an existing JSON """
""" file. Currently, the JSON file is from                             """
""" https://data.cdc.gov/api/views/cjae-szjv/rows.json?accessType=DOWNLOAD """
""" and the associated values are configured to this dataset. """
""" Specifically, the data is stored in a dictionary, which holds """
""" a tag specifying if the block is free and can be overwritten (which is """
""" initialized to false). Other items stored in the values itself is a """
""" dictionary which includes an id associated with the measurement, type """
""" of measurement, an id associated with a specific state, that state's """
""" name, an id associated with a county, that county's name, year of """
""" measurement, and if there are any units, then its name and symbol. """
def setUpDatabase(filename):
    # Open and load the file (the with clause ensures the file closes,
    # even if there is an exception raised).
    with open(filename, 'r') as airMeasurementsJSON:
        airMeasurements = json.load(airMeasurementsJSON)
    assert airMeasurementsJSON.closed

    # Set up the key value store dictionary, which is
    # written to the file at a later point.
    measurementStore = {}
    positionCounter = 0
    for measurement in airMeasurements['data']:
        # Free or not? 0 indicates not free, 1 indicates free
        items = dict(isFree='false', position=positionCounter)
        values = dict()
        values['measureId'] = measurement[8]
        values['measureDesc'] = measurement[9]
        values['stateId'] = measurement[12]
        values['stateName'] = measurement[13]
        values['countyId'] = measurement[14]
        values['countyName'] = measurement[15]
        values['year'] = measurement[16]
        values['measurement'] = measurement[17]
        if measurement[18] != "No Units":
            values['units'] = measurement[18]
            values['unitSymbol'] = measurement[19]
        items['data'] = values
        measurementStore[measurement[0]] = items
        positionCounter += 1
    return measurementStore


""" loadFile checks if the storageDBFile exists. If it doesn't, """
""" then the key value store doesn't exist yet, and the defaultFile """
"""(the json file for reading) is to be used if there is a valid path to """
""" it. If there is no valid path, the user is given the url to retrieve """
""" the default file and the name required for the program to run. """
""" If the storage file exists, then the file is read. In any case, the """
""" information is read to the key value store running in the program. """
""" The return values are the key value store, whether the storageDBFile """
""" exists yet, and the maximum position read from in the case the """
""" storageDBFile exists. """
def loadFile(defaultFile, storageDBFile, isNewDBFile, maximumPosition):
    dynamicDB = {}
    if os.path.isfile(storageDBFile):
        with open(storageDBFile, 'rb') as file:
            rows = [line.strip().decode('utf-8').replace('\0', '') for line
                    in file if line.strip()]
        for row in rows:
            dynamicDB.update(ast.literal_eval(row))
        lastKey = ast.literal_eval(rows[-1])
        for key in lastKey.keys():
            maximumPosition = lastKey[key]['position']
    else:
        isNewDBFile = True
        if os.path.isfile(defaultFile):
            dynamicDB = setUpDatabase(defaultFile)
        else:
            raise Exception('Need json file from '
                            'https://data.cdc.gov/api/views/cjae-'
                            'szjv/rows.json?accessType=DOWNLOAD for setup! '
                            'Title it AirQualityMeasures.json.')
    return dynamicDB, isNewDBFile, maximumPosition


""" saveChanges saves the currently running key value store """
""" to the storage file (which will be created if necessary). """
""" The indices of the deleted keys are stored in a list, which """
""" are then passed to updateFileWithDeletes to delete from """
""" the storage file. Next, for every "key" that was updated, """
""" the index of the key (from the list of keys """
""" obtained from the dictionary), the key itself, and its value """
""" are stored in a list, which is used to update the corresponding line in """
""" the storage file, and finally, the list of inserted rows is passed to """
""" the updateFileWithInserts, where the information is written to the """
""" end of the file. """
def saveChanges(isNewDBFile, storageDBFile, dynamicDB,
                positionsDeleted, insertedRows, updatedRows):
    # Once the key value store is to be closed, we save any changes.
    # If the key value store file didn't exist yet, then
    # a new one is created here.
    c = 0
    if isNewDBFile:
        with open(storageDBFile, 'wb') as file:
            for item in dynamicDB:
                toWrite = '{' + json.dumps(item) + ': ' + \
                              json.dumps(dynamicDB[item]) + '}' + '\n'
                toByte = toWrite.encode('utf-8')
                file.write(('\0' * (blockSize - sys.getsizeof(toByte)))
                               .encode('utf-8'))
                file.write(toByte)
                c += 1
    # note: This only works in Python 3.7+. Otherwise, we would
    # need to use something like orderedDict
    keyList = list(dynamicDB.keys())
    indicesToDelete = []
    updateInfo = []
    for each in positionsDeleted:
        # The position is a marker if the item was loaded from the
        # file. If the item was not loaded from the file
        # and is being deleted, then we cannot delete it
        # from the storage file
        if 'position' in dynamicDB[each]:
            indicesToDelete.append(keyList.index(each))
        else:
            # Otherwise, we were originally going to insert
            # this value, so we want to make sure that this
            # is not written to the file.
            del insertedRows[each]
    # We need the index for each row so we know which lines to modify.
    for each in updatedRows:
        updateInfo.append((keyList.index(each), each, dynamicDB[each]))
    updateFileWithUpdates(storageDBFile, updateInfo)
    updateFileWithDeletes(storageDBFile, indicesToDelete)
    updateFileWithInserts(storageDBFile, insertedRows, maximumPosition)


""" The main function checks if a file exists that contains the key value """
""" store, and if it does, then we load the store from the file. Otherwise, """
""" one is initialized from a JSON file (as the store is configured around """
""" a specific JSON file storing air quality measurements. This main """
""" function will ideally hold handling user input and other operations """
""" necessary, and when the key value store is closed, any changes are """
""" written to the file which stores the key value store. """
if __name__ == "__main__":
    print("Loading...\n")
    # dynamicDB = {}
    defaultFile = 'AirQualityMeasures.json'
    storageDBFile = 'AirQualityDBStore.bin'
    isNewDBFile = False
    insertedRows = {}
    positionsDeleted = []
    updatedRows = {}
    maximumPosition = 0
    replacedRows = {}
    # Load existing key value file, into a dictionary,
    # or create a new dictionary loaded to the file
    # later.
    dynamicDB, isNewDBFile, maximumPosition = \
        loadFile(defaultFile, storageDBFile, isNewDBFile, maximumPosition)

    # This section handles user input and passes it to
    # the handleInput function to change the key value
    # store.
    toSave = True
    while True:
        n = input("Welcome to AirQualityStoreDB! Exit with exit or quit if you"
                  " want your changes saved, or with abort if you don't.\n")
        if n == "quit" or n == "abort" or n == "exit":
            if n == "abort":
                toSave = False
            break
        # This allows to save or abandon changes to the file without
        # exiting the program.
        if n == "save" or n == "undo":
            # saving is pretty simple as much of the logic
            # is handled in saveChanges(). We must remember to
            # clear the values that keep track of changes
            # to the key-value store as those changes
            # have been saved.
            if n == "save":
                saveChanges(isNewDBFile, storageDBFile, dynamicDB,
                            positionsDeleted, insertedRows, updatedRows)
                for each in positionsDeleted:
                    del dynamicDB[each]
            # undo is trickier, as we need to not only get rid of
            # inserted rows and reset deleted values to "not free",
            # but also we need to undo the updates. To do so,
            # we keep track of the values that have been replaced.
            # We rewrite the data to be that of the "replaced" rows.
            else:
                # TODO: Finish debugging for all cases
                for each in insertedRows:
                    del dynamicDB[each]

                for each in positionsDeleted:
                    dynamicDB[each]['isFree'] = 'false'

                for each in updatedRows:
                    dynamicDB[each] = replacedRows[each]

            # The applicable changes have been saved to the
            # storage file, so we no longer need them.
            insertedRows.clear()
            positionsDeleted.clear()
            updatedRows.clear()
            replacedRows.clear()
            continue

        newRows = handleInput(n, dynamicDB)
        # If items were deleted, then we mark their corresponding rows as
        # invalid data.
        if newRows is not None and len(newRows) > 0:
            # This is for the updated values, so we can store
            # in a way it makes updating easier.
            if newRows[2] is not None and len(newRows[2]) > 0:
                if newRows[2][0] is not None and len(newRows[2][0]) > 0:
                    for key in newRows[2][0]:
                        # If this is a new row (inserted after loading the
                        # storage
                        # file), then we simply change the inserted value.
                        if key in insertedRows:
                            insertedRows[key] = newRows[2][0][key]
                        else:
                            updatedRows.update(newRows[2][0])
                            replacedRows.update(newRows[2][1])
                        print("Successfully updated ", key, ": ",
                             dynamicDB[key]['data'], "\n")
            # This is for the deleted values, so we can store
            # in a way it makes updating easier.
            if newRows[1] is not None and len(newRows[1]) > 0:
                for item in newRows[1]:
                    dynamicDB[item]['isFree'] = 'true'
                    # This is in the storage file, so
                    # we should erase them.
                    if 'position' in dynamicDB[item]:
                        positionsDeleted.append(item)
                    else:
                        # This was a new row, so we do not
                        # want to write this to the file.
                        del insertedRows[item]
                    # If there were rows updated, we
                    # want to make sure these aren't
                    # written to the file because they
                    # were deleted.
                    if item in updatedRows:
                        del updatedRows[item]
                    print("Successfully deleted ", item, ": ",
                          dynamicDB[item]['data'], "\n")
            # If items were inserted, then we add them to our local
            # key value store and update the list with
            # the rows to insert.
            if newRows[0] is not None and len(newRows[0]) > 0:
                dynamicDB.update(newRows[0])
                insertedRows.update(newRows[0])
                for key in newRows[0]:
                    print("Successfully inserted ", key, ": ",
                          newRows[0][key]['data'], "\n")
    if toSave:
        saveChanges(isNewDBFile, storageDBFile, dynamicDB,
                positionsDeleted, insertedRows, updatedRows)
    print("Goodbye! Hope to see you again soon!")