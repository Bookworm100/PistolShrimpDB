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
            'countyName', 'Year', 'Measurement', 'Units', 'Unit Symbol'}

""" performTempDeletion removes the values or values assicated with the key """
""" from the dictionary holding the database, and keep track of what might """
""" be removed from the storage file upon exiting or quitting. """
def performTempDeletion(key, values):
    return {}

""" generateNewRows will insert the new values to the dictionary key value """
""" store, and keep track of what should get added to the storage file """
""" upon exiting or quitting. """
def generateNewRows(colValList):
    return {}

""" generateRandomKey generates a random key to be used when inserting new """
""" values to the dictionary key value store. """
def generateRandomKey():
    key = 'row-'.join(random.choices(string.ascii_letters +
                                     string.digits, k=4))
    key = key.join(random.choices('!@#$%^&~_-.+=', k=1))
    key = key.join(random.choices(string.ascii_letters + string.digits, k=4))
    key = key.join(random.choices('!@#$%^&~_-.+=', k=1))
    key = key.join(random.choices(string.ascii_letters + string.digits, k=4))
    return key

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
    key = ''
    values = {}
    if matches[0].lower() == 'insert':
        if matches[2].lower() == 'with' and matches[3].lower() == 'values'\
                and len(matches) >= 5:
            # check if key already exists in the key value store
            if key in dynamicDB:
                print("Key already in key value store. Selecting new random "
                      "key instead...\n")
                while key in dynamicDB:
                    key = generateRandomKey()
            else:
                # TODO: support input keys with alphanumeric instead of letters
                key = matches[1].lower()
            matches = matches[4:]
            values = generateNewRows(matches)
        elif matches[1].lower() == 'values' and len(matches) >= 3:
            matches = matches[2:]
            values = generateNewRows(matches)
        else:
            print("Insert format is incorrect. Usage:\n INSERT [key] WITH "
                  "VALUES (col=tag, col2=tag2...) \n INSERT VALUES (col=tag,"
                  " col2=tag2, col3=tag3...)")
            return {}
        return values
    elif matches[0].lower() == 'delete':
        if matches[1].lower() == 'values' and len(matches) == 3:
            matches = matches[2:]
        elif len(matches) == 2:
            if key in dynamicDB:
                key = m[1].lower()
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
        values['Year'] = measurement[16]
        values['measurement'] = measurement[17]
        if measurement[18] != "No Units":
            values['Units'] = measurement[18]
            values['Unit Symbol'] = measurement[19]
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
                file.write(toByte)
                file.seek(c * blockSize + blockSize - sys.getsizeof(toByte))
                c += 1
    # TODO: implement based on changes
    # else: