# Import statements:
# The documents we're using require JSON
import os.path
import json
import ast
from jsonpath_ng import jsonpath, parse

class inputFile:

    def __init__(self, name, whereKey, whereData):
        self.filename = name
        self.dynamicDB = {}
        self.isNewDBFile = False
        self.maximumPosition = 0
        self.whereKey = whereKey
        self.whereData = whereData
        self.typesSet = []
        self.name, self.type = os.path.splitext(name)

    """ If the places to find the data is specified, all that's required is to see if """
    """ it's in the dictionary. Otherwise, we search for a suitable candidate () """
    """ because we don't know what the user wants, we simply look for a """
    """ viable candidate by searching for the largest element in the dictionary """
    """ or list. """
    def findTheData(self, measurements):
        data = None
        if self.whereData in measurements or self.whereData != 'data':
            if self.whereData in measurements:
                data = measurements[self.whereData]
            else:
                for elem in measurements:
                    jsonpathExpr = parse(elem + self.whereData)
                    jsonMatches = jsonpathExpr.find(measurements)
                    if len(jsonMatches) != 0:
                        data = jsonMatches
                        break
        if data is None:
            findData = None
            data = measurements
            if len(measurements) > 0 and type(measurements) == list:
                # singleton element in form of list/dict possible
                # needs to be list of lists or dictionaries
                # if just one giant list of dictionaries, make into one row
                findData = max(measurements, key=len)
                findData = measurements.index(findData)
            elif len(measurements) > 0 and type(measurements) == dict:
                # value needs to be list of lists or dictionaries
                findData = max(measurements, key=lambda d: len(measurements[d]))

            if findData is not None:
                data = measurements[findData]
            while type(data) == dict and len(data) == 1:
                data = data[list(data.keys())[0]]
            if type(data) == dict:
                self.typesSet = list(data.keys())
                data = list(data.values())
            elif type(data) != list:
                data = [data]
        return data

    """ 1. Find the whereKey in the measurements, which should give us a list of columns if possible """
    """ 2. Fine where the data is: """
    """ 3. If the data doesn't exist, this is a problem and an exception should be raised. """
    """ 4. If the whereKey was found in Step 1, extract them by filtering out metadata """
    """ 5. If not 4, then set the column names to be default values."""
    def retrieveColumnsData(self, measurements):
        # Search for the list of columns using jsonpath_ng's parse
        skipItems = 0
        jsonpathExpr = parse('meta..' + self.whereKey)
        jsonMatches = []
        for elem in measurements:
            jsonMatches = jsonpathExpr.find(measurements)
            if len(jsonMatches) == 0:
                jsonpathExpr = parse(elem + '..' + self.whereKey)
            else:
                break

        # Find where the data is if not specified (or incorrectly specified)
        data = self.findTheData(measurements)

        # There should be at least some data, and the file should not
        # be empty.
        if data is None or len(data) == 0:
            raise Exception("Something went wrong with the loading of the data. Please try again.")

        # If the columns were found, we set them to be uniformly lowercase
        # and we process them to help us load the data to make
        # it accessible from the program, and filter out non-human readable
        # metadata that interferes with the program.
        if len(jsonMatches) > 0:
            vals = [match.value for match in jsonpathExpr.find(measurements)]
            originalLength = len(vals)
            self.typesSet = [val['name'].lower() for val in vals[0] if 'id' not in val or val['id'] != -1]
            skipItems = originalLength - len(vals) - 1
        # If they were not found, we set default values that can be renamed
        elif len(self.typesSet) == 0:
            maxVal = max(data, key=len)
            self.typesSet = ["column" + str(i) for i in range(len(maxVal))]

        return data, skipItems


    """ setUpDatabase2 initilizes the key value store from an existing JSON """
    """ file. """
    """ Specifically, the data is stored in a dictionary, which holds """
    """ a tag specifying if the block is free and can be overwritten (which is """
    """ initialized to false). Other items stored in the values itself is a """
    """ dictionary which includes an id associated with the measurement, type """
    """ of measurement, an id associated with a specific state, that state's """
    """ name, an id associated with a county, that county's name, year of """
    """ measurement, and if there are any units, then its name and symbol. """
    """ @param: fileName, the name of the json file to load the initial rows """
    """         from """
    """ @return: measurementStore, the newly set up key value store, to be """
    """          dynamicDB (see loadFile)"""

    def setUpDatabase(self):
        # Open and load the file (the with clause ensures the file closes,
        # even if there is an exception raised).
        # filename = 'leadingCauses.json'
        with open(self.filename, 'r') as measurementsJSON:
            try:
                measurements = json.load(measurementsJSON)
            except json.JSONDecodeError:
                raise Exception("Please check the format of your JSON file!")
        assert measurementsJSON.closed

        # Retrieve column values, which by default is "column1", "column2", etc
        data, skipItems = self.retrieveColumnsData(measurements)

        # Set up the key value store dictionary, which is
        # written to the file at a later point.
        measurementStore = {}
        positionCounter = 0
        for measurement in data:
            # Free or not? 0 indicates not free, 1 indicates free
            items = dict(isFree='false', position=positionCounter)
            values = dict()
            for itm, type1 in zip(range(skipItems, len(self.typesSet) + skipItems), self.typesSet):
                values[type1] = measurement[itm]
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
    """ @param: defaultFile: if there is no currently existing database file, """
    """         we want to load from a file with the original json values. """
    """ @param: storageDBFile, the name of the file storing the rows  """
    """ @param: isNewDBFile, a boolean indicating if the file is new """
    """ @param: maximumPosition, the final position in the file, incremented """
    """         with each inserted row """
    """ @return: dynamicDB, the key value store maintained in the program """
    """          that is now setup and initialized by the program """
    """ @return: isNewDBFile, a false value indicating that if the file """
    """          did not exist earlier, it now does """
    """ @return: maximumPosition the final position in the file, incremented """
    """         with each inserted row """

    def loadFile(self):
        dynamicDB = {}
        # Load from a preexisting storage file.
        if self.type == '.bin':
            # Read from the file, line by line (row by row).
            with open(self.filename, 'rb') as file:
                rows = [line.strip().decode('utf-8').replace('\0', '') for line
                        in file if line.strip()]
            # Load each row to the store maintained in the program.
            # ast cannot read null characters, so we have to replace them
            for row in rows:
                if 'null' in row:
                    row = row.replace('null', "None")
                dynamicDB.update(ast.literal_eval(row))
            # Update maximum position, which is helpful to
            # note when adding, removing, and updating
            # rows.
            lastKey = ast.literal_eval(rows[-1])
            for key in lastKey.keys():
                self.maximumPosition = lastKey[key]['position']
        # Load from a JSON file
        elif self.type == '.json':
            # We are creating a new file.
            self.isNewDBFile = True
            # Check the file actually exists
            if os.path.isfile(self.filename):
                dynamicDB = self.setUpDatabase()
            else:
                raise Exception('Need json file that exists in the path specified!')
        else:
            raise Exception('Unknown data type file!')

        return dynamicDB, self.isNewDBFile, self.maximumPosition, self.typesSet