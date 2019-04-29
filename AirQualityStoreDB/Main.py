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


""" updateFileWithDeletes removes items marked for deletion in the key """
""" value store from the storage file. As Python 3.7 preserves order """
""" in dictionaries, it's possible to recall the positions of keys (in the """
""" storage file) to be deleted by """
""" using simple Python function calls (handled in the main function). """
""" The list of these indices is the argument."""
def updateFileWithDeletes(storageDbFile, indicesDeleted):
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
        for colIndex in range(0, len(values), 2):
            col = values[colIndex]
            val = values[colIndex + 1]
            selected = {}
            for item1 in filterItems:
                if col in filterItems[item1]['data']:
                    if filterItems[item1]['data'][col] == val:
                        newVal = {}
                        newVal[item1]=filterItems[item1]
                        selected.update(newVal)
            filterItems = selected
        for item in filterItems:
            selectedKeys.append(item)
    return selectedKeys


""" generateNewRows will insert the new values to the dictionary key value """
""" store, and keep track of what should get added to the storage file """
""" upon exiting or quitting. """
def generateNewRows(colValList):
    # TODO: Should I enforce id/name restriction?
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

""" This isn't quite completed just yet, but this should handle anything """
""" with updates. """
def handleUpdates(matches, dynamicDB):
    print("Not yet implemented!")

""" This isn't quite completed just yet, but this should handle anything """
""" with searches. """
def handleSearches(matches, dynamicDB):
    print("Not yet implemented!")

""" This isn't quite completed just yet, but this should handle anything """
""" with selects. """
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
def handleSelects(matches, dynamicDB):
    # return nothing
    # TODO: Finish implementing with more complicated selects.
    if matches[1] == '*':
        if len(matches) == 2 or (len(matches) == 4 and
                                 matches[2].lower() == 'from' and
                                 matches[3].lower() == 'keys'):
            # This is the SELECT * FROM all keys
            with open('allKeys.txt', 'w') as file:
                for item in dynamicDB:
                    if dynamicDB[item]['isFree'] == 'false':
                        toWrite = json.dumps(item) + '\n'
                        file.write(toWrite)
        elif len(matches) == 4 and (matches[2].lower() == 'from' and
                                    matches[3].lower() == 'values'):
            with open('allValues.txt', 'w') as file:
                for item in dynamicDB:
                    if dynamicDB[item]['isFree'] == 'false':
                        toWrite = json.dumps(dynamicDB[item]['data']) + '\n'
                        file.write(toWrite)
        elif len(matches) == 4 and (matches[2].lower() == 'from' and
                                    matches[3].lower() == 'all'):
            with open('allKeysValues.txt', 'w') as file:
                for item in dynamicDB:
                    if dynamicDB[item]['isFree'] == 'false':
                        toWrite = '{' + json.dumps(item) + ': ' + \
                              json.dumps(dynamicDB[item]['data']) + '}' + '\n'
                        file.write(toWrite)
    elif (len(matches) == 2) or (len(matches) == 4 and
                                 matches[2].lower() == 'from' and
                                 matches[3].lower() == 'all'):
        if matches[1].lower() in dynamicDB and dynamicDB[matches[1].lower()]\
                    ['isFree'] == 'false':
            print(dynamicDB[matches[1].lower()]['data'], '\n')
        else:
            print("The key is not in the store!")
    else:
        print("This part is not implemented yet!\n")


""" handleDeletes passes either a key or a set of values to the function """
""" marking keys for deletion. The matches generated using regex are used """
""" for this purpose. If a key is not in the store, then a message """
""" explaining this is printed out. If the format is incorrect (not """
""" as DELETE [key], or DELETE VALUES (col=tag, col2=tag2, col3=tag3….) """
""" a usage is printed out, and the current operation is abandoned. """
def handleDeletes(matches, dynamicDB):
    key = ''
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
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+]+', re.IGNORECASE)
    matches = parser.findall(command)
    key = ''
    values = {}
    if matches[0].lower() == 'insert':
        return handleInserts(matches, dynamicDB), []
    elif matches[0].lower() == 'delete':
        return {}, handleDeletes(matches, dynamicDB)
    elif matches[0].lower() == 'select':
        handleSelects(matches, dynamicDB)
    elif matches[0].lower() == 'search':
        handleSearches(matches, dynamicDB)
    elif matches[0].lower() == 'update':
        handleUpdates(matches, dynamicDB)
    return {}, []

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


""" The main function checks if a file exists that contains the key value """
""" store, and if it does, then we load the store from the file. Otherwise, """
""" one is initialized from a JSON file (as the store is configured around """
""" a specific JSON file storing air quality measurements. This main """
""" function will ideally hold handling user input and other operations """
""" necessary, and when the key value store is closed, any changes are """
""" written to the file which stores the key value store. """
if __name__ == "__main__":
    print("Loading...\n")
    dynamicDB = {}
    defaultFile = 'AirQualityMeasures.json'
    storageDBFile = 'AirQualityDBStore.bin'
    isNewDBFile = False
    insertedRows = {}
    positionsDeleted = []
    maximumPosition = 0
    # Load existing key value file, into a dictionary,
    # or create a new dictionary loaded to the file
    # later.
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
        newRows = handleInput(n, dynamicDB)
        # If items were deleted, then we mark their corresponding rows as
        # invalid data.
        if newRows is not None and len(newRows) > 0:
            if len(newRows[1]) > 0:
                for item in newRows[1]:
                    dynamicDB[item]['isFree'] = 'true'
                    if 'position' in dynamicDB[item]:
                        positionsDeleted.append(item)
                    else:
                        del insertedRows[item]
                    print("Successfully deleted ", item, ": ",
                          dynamicDB[item]['data'], "\n")
            # If items were inserted, then we add them to our local
            # key value store and update the list with
            # the rows to insert.
            if len(newRows[0]) > 0:
                dynamicDB.update(newRows[0])
                insertedRows.update(newRows[0])
                for key in newRows[0]:
                    print("Successfully inserted ", key, ": ",
                          newRows[0][key]['data'], "\n")
    # Once the key value store is to be closed, we save any changes.
    # If the key value store file didn't exist yet, then
    # a new one is created here.
    if toSave:
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
                    #file.seek(c * blockSize + blockSize - sys.getsizeof(toByte))
                    c += 1
        # TODO: Is it ok if the deletion depends on the implementation
        # of Python 3.7?
        # note: This only works in Python 3.7+. Otherwise, we would
        # need to use something like orderedDict
        keyList = list(dynamicDB.keys())
        indicesToDelete = []
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
        updateFileWithDeletes(storageDBFile, indicesToDelete)
        updateFileWithInserts(storageDBFile, insertedRows, maximumPosition)
    print("Goodbye! Hope to see you again soon!")