# Import statements:
# The documents we're using require JSON
import os.path
import json
import sys
import ast

# size of blocks of memory in bytes
blockSize = 1000

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
    dynamicDB = {}
    defaultFile = 'AirQualityMeasures.json'
    storageDBFile = 'AirQualityDBStore.bin'
    # load existing key value file, into a dictionary,
    # or create a new dictionary loaded to the file
    # later.
    if os.path.isfile(storageDBFile):
        with open(storageDBFile, 'rb') as file:
            rows = [line.strip().decode('utf-8').replace('\0', '') for line
                    in file if line.strip()]
        for row in rows:
            dynamicDB.update(ast.literal_eval(row))
    else:
        if os.path.isfile(defaultFile):
            dynamicDB = setUpDatabase(defaultFile)
        else:
            raise Exception('Need json file from '
                            'https://data.cdc.gov/api/views/cjae-'
                            'szjv/rows.json?accessType=DOWNLOAD for setup! '
                            'Title it AirQualityMeasures.json.')

    # TODO:
    # Ideally we'd allow for user input and necessary
    # operations at this point

    # Once the key value store is to be closed, we save any changes.
    # TODO: only save changes instead of rewriting the whole file
    filename = 'itemsBin.bin'
    c = 0
    with open(filename, 'wb') as file:
        for item in dynamicDB:
            toWrite = '{' + json.dumps(item) + ': ' + \
                    json.dumps(dynamicDB[item]) + '}' + '\n'
            toByte = toWrite.encode('utf-8')
            file.write(toByte)
            file.seek(c * blockSize + blockSize - sys.getsizeof(toByte))
            c += 1