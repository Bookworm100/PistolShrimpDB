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

""" For now, we are just appending to the end of the file. Once delete """
""" is fully implemented, the data will be changed to read/write where tags """
""" are 0, and then appending afterwards. (Positions where deletions """
""" happened will need to be recorded). """
def updateFileWithInserts(storageDbFile, insertedRows):
    # TODO: Change insert to depend on the output from delete
    with open(storageDbFile, 'a+b') as file1:
        for item1 in insertedRows:
            toWrite1 = '{' + json.dumps(item1) + ': ' + \
                       json.dumps(insertedRows[item1]) + '}' + '\n'
            toByte1 = toWrite1.encode('utf-8')
            file1.write(('\0'*(blockSize-sys.getsizeof(toByte1)))
                        .encode('utf-8'))
            file1.write(toByte1)

""" performTempDeletion removes the values or values assicated with the key """
""" from the dictionary holding the database, and keep track of what might """
""" be removed from the storage file upon exiting or quitting. """
def performTempDeletion(key, values):
    return {}

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

def handleUpdates(matches, dynamicDB):
    print("Not yet implemented!")

def handleSearches(matches, dynamicDB):
    print("Not yet implemented!")

def handleSelects(matches, dynamicDB):
    # return nothing
    # TODO: Finish implementing with more complicated selects.
    if matches[1] == '*':
        if len(matches) == 2 or (len(matches) == 4 and
                                 matches[2].lower() == 'from' and
                                 matches[3].lower() == 'keys'):
            # This is the SELECT * FROM all keys
            # TODO: might write to file instead
            with open('allKeys.txt', 'w') as file:
                for item in dynamicDB:
                    toWrite = json.dumps(item) + '\n'
                    file.write(toWrite)
            # for item in dynamicDB:
            #    print(item, ", ")
        elif len(matches) == 4 and (matches[2].lower() == 'from' and
                                    matches[3].lower() == 'values'):
            with open('allValues.txt', 'w') as file:
                for item in dynamicDB:
                    toWrite = json.dumps(dynamicDB[item]) + '\n'
                    file.write(toWrite)
            # for item in dynamicDB:
            #    print(dynamicDB[item], ", ")
        elif len(matches) == 4 and (matches[2].lower() == 'from' and
                                    matches[3].lower() == 'all'):
            with open('allKeysValues.txt', 'w') as file:
                for item in dynamicDB:
                    toWrite = '{' + json.dumps(item) + ': ' + \
                              json.dumps(dynamicDB[item]) + '}' + '\n'
                    file.write(toWrite)
    elif (len(matches) == 2) or (len(matches) == 4 and
                                 matches[2].lower() == 'from' and
                                 matches[3].lower() == 'all'):
        if matches[1].lower() in dynamicDB:
            print(dynamicDB[matches[1].lower()], '\n')
        else:
            print("The key is not in the store!")
    else:
        print("This part is not implemented yet!\n")

def handleDeletes(matches, dynamicDB):
    if matches[1].lower() == 'values' and len(matches) >= 3:
        matches = matches[2:]
    elif len(matches) == 2:
        if matches[1].lower() in dynamicDB:
            key = matches[1].lower()
            matches = matches[1]
        else:
            print("The key is not in the store!")
            return {}
    else:
        print("Delete format is incorrect. Usage:\n DELETE [key] "
              " \n DELETE VALUES (col=tag,"
              " col2=tag2, col3=tag3...)")
        return {}
    performTempDeletion(key, matches)
    return {}

def handleInserts(matches, dynamicDB):
    key = ''
    values = {}
    if matches[2].lower() == 'with' and matches[3].lower() == 'values' \
            and len(matches) >= 5:
        # check if key already exists in the key value store
        key = matches[1].lower()
        if key in dynamicDB:
            print("Key already in key value store. Selecting new random "
                  "key instead...\n")
            while key in dynamicDB:
                key = generateRandomKey()
        matches = matches[4:]
        values = generateNewRows(matches)
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
    # TODO: Chop up this function to helper functions. It's getting long.
    # check the inputs
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+]+', re.IGNORECASE)
    matches = parser.findall(command)
    key = ''
    values = {}
    if matches[0].lower() == 'insert':
        return handleInserts(matches, dynamicDB)
    elif matches[0].lower() == 'delete':
        return handleDeletes(matches, dynamicDB)
    elif matches[0].lower() == 'select':
        handleSelects(matches, dynamicDB)
    elif matches[0].lower() == 'search':
        handleSearches(matches, dynamicDB)
    elif matches[0].lower() == 'update':
        handleUpdates(matches, dynamicDB)

    # TODO: output may need to include deleted rows too and/or their positions
    return {}

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
    for measurement in airMeasurements['data']:
        # Free or not? 0 indicates not free, 1 indicates free
        items = dict(isFree='false')
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
    # Change this before committing
    storageDBFile = 'AirQualityDBStore.bin'
    isNewDBFile = False
    insertedRows = {}
    # Load existing key value file, into a dictionary,
    # or create a new dictionary loaded to the file
    # later.
    if os.path.isfile(storageDBFile):
        with open(storageDBFile, 'rb') as file:
            rows = [line.strip().decode('utf-8').replace('\0', '') for line
                    in file if line.strip()]
        for row in rows:
            dynamicDB.update(ast.literal_eval(row))
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
        dynamicDB.update(newRows)
        insertedRows.update(newRows)
        if newRows != {}:
            print("Successfully inserted ",newRows, "\n")

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
                    file.write(toByte)
                    file.seek(c * blockSize + blockSize - sys.getsizeof(toByte))
                    c += 1
        # TODO: Finish implementing based on changes
        # deletions come first as they update the tags
        updateFileWithInserts(storageDBFile, insertedRows)