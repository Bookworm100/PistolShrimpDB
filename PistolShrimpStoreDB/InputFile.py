# Import statements:
# The documents we're using require JSON
import os.path
import json
import ast
from jsonpath_ng import parse

""" Module: InputFile
    Description: holds all information relating to the input file, especially
                 the initial loading of either a json file or existing storage
                 file
    Classes: InputFile
"""


class inputFile:
    """ inputFile Class holds all information relating to the input file,
    especially the initial loading of either a json file or existing storage file

       Variables:
       filename - the name of the file to load
       dynamicDB - the key value store to be initially set up
       isNewDBFile - a flag indicating if a storage file needs to be entirely
                     written. In the case the storage file already exists,
                     adding a new Json file will overwrite it in case the user
                     wants to load in a new dataset.
       maximumPosition - an integer value indicating whether the row is part of
                         the storage file already (for JSON files that are
                         loaded), the maximumPosition for any row will not exist.
       whereKey - a marker of where to look for column/key types
       whereData - a marker of where to look for data
       typesSet - a list of column types that are loaded
       name - the name of the file to be loaded without its location
       type - the location of the file to be loaded

       Functions:
       findTheData: locates a source of data (either through a keyword specified
                    or through looking for the largest length of text in the
                    highest level dictionary or list)
       retrieveColumnsData: locates the columns by using a keyword specified by
                            the user if they wish or use a default labeling, and
                            calls find the data, and they retrieve the column
                            labels and data to use
       setupDatabase: sets up the initial key value store if it doesn't exist
       loadFile: loads either the existing storage file or a JSON file specified
                 and in doing so, sets up the intiial key value store
       """

    def __init__(self, name, whereKey, whereData):
        self.filename = name
        self.dynamicDB = {}
        self.isNewDBFile = False
        self.maximumPosition = 0
        self.whereKey = whereKey
        self.whereData = whereData
        self.typesSet = []
        self.name, self.type = os.path.splitext(name)


    def findTheData(self, measurements):
        """ findTheData retrieves a viable candidate for data.

        If the places to find the data is specified, all that's required is to
        see if it's in the dictionary. Otherwise, we search for a suitable
        candidate because we don't know what the user wants. To do so, we
        we simply look for a viable candidate by searching for the largest
        element in the dictionary or list.

        Keyword arguments:
        measurements - the loaded JSON data

        Return values:
        data - the viable data set extracted from the JSON file
        """
        data = None
        if self.whereData in measurements or self.whereData != 'data':
            # We search for data in the loaded JSON data
            if self.whereData in measurements:
                data = measurements[self.whereData]
            else:
                # If the data is hidden somewhere in the structure,
                # we use the json parse function to search for
                # descendants of the keyword (by default it is meta..data)
                for elem in measurements:
                    jsonpathExpr = parse(elem + '..' + self.whereData)
                    jsonMatches = jsonpathExpr.find(measurements)
                    if len(jsonMatches) != 0:
                        data = jsonMatches
                        break

        # If we still can't find data, we search for the largest element
        # in the list or dictionary that is loaded.
        if data is None:
            findData = None
            data = measurements
            if len(measurements) > 0 and type(measurements) == list:
                # Extracting the largest element from the list
                findData = max(measurements, key=len)
                findData = measurements.index(findData)
            elif len(measurements) > 0 and type(measurements) == dict:
                # Extracting the largest element from the dictionary
                findData = max(measurements, key=lambda d: len(measurements[d]))

            # We convert the data to an accepetable format (list of
            # lists or dictionary).
            if findData is not None:
                # Extract data if we got a large blob
                data = measurements[findData]
            # Try to extract the data from the "data" as it's
            # likely encapsulating
            while type(data) == dict and len(data) == 1:
                data = data[list(data.keys())[0]]
            # Make a list of data values in case "data" is
            # a dict
            if type(data) == dict:
                self.typesSet = list(data.keys())
                data = list(data.values())
            # In case we have singleton elements, make them into
            # a list.
            elif type(data) != list:
                data = [data]
        return data

    def retrieveColumnsData(self, measurements):
        """ retrieveColumnsData retrieves the columns and data from the loaded
        JSON data (measurements).

        This happens in the following steps:
        1. Find the whereKey in the measurements, which should give us a list of columns if possible
        2. Fine where the data is:
        3. If the data doesn't exist, this is a problem and an exception should be raised.
        4. If the whereKey was found in Step 1, extract them by filtering out metadata
        5. If not 4, then set the column names to be default values.

        Keyword Arguments:
        measurements - the loaded JSON data

        Return values:
        (data, skipItems) - the obtained data and skipItems, a value indicating
                            number of items to skip (if possible), which is
                            usually metadata

        """
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
            raise Exception("Something went wrong with the loading of the data. "
                            "Please try again, and check your file for any anomalies.")

        # If the columns were found, we set them to be uniformly lowercase
        # and we process them to help us load the data to make
        # it accessible from the program, and filter out non-human readable
        # metadata that interferes with the program.
        if len(jsonMatches) > 0:
            vals = [match.value for match in jsonpathExpr.find(measurements)]
            originalItems = [val['name'].lower() for val in vals[0]]
            self.typesSet = [val['name'].lower() for val in vals[0]
                             if 'id' not in val or val['id'] != -1]
            skipItems = len(originalItems) - len(self.typesSet)
        # If they were not found, we set default values that can be renamed
        elif len(self.typesSet) == 0:
            maxVal = max(data, key=len)
            self.typesSet = ["column" + str(i) for i in range(len(maxVal))]

        return data, skipItems


    def setUpDatabase(self):
        """setUpDatabase initilizes the key value store from an existing JSON
        file.
        Specifically, the data is stored in a dictionary, which holds
        a tag specifying if the block is free and can be overwritten (which is
        initialized to false). Other items stored in the values itself is a
        dictionary which includes an id associated with the measurement, type
        of measurement, an id associated with a specific state, that state's
        name, an id associated with a county, that county's name, year of
        measurement, and if there are any units, then its name and symbol.

        No keyword arguments as everything is derived from class

        Return value:
        measurementStore -  the newly set up key value store, to be
                  dynamicDB (see loadFile)
        """

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

    def loadFile(self):
        """ loadFile loads either an existing storage file or a JSON file to
        load to a new storage file.

        loadFile checks if the storageDBFile exists. If it doesn't,
        then the key value store doesn't exist yet, and the defaultFile
        (the json file for reading) is to be used if there is a valid path to
        it. If there is no valid path, the user is given the url to retrieve
        the default file and the name required for the program to run.
        If the storage file exists, then the file is read. In any case, the
        information is read to the key value store running in the program.
        The return values are the key value store, whether the storageDBFile
        exists yet, and the maximum position read from in the case the
        storageDBFile exists.

        No keyword arguments as everything is derived from class

        Return values:
        dynamicDB -  the key value store maintained in the program
                  that is now setup and initialized by the program
        isNewDBFile -  a false value indicating that if the file
                  did not exist earlier, it now does
        maximumPosition - the final position in the file, incremented
                 with each inserted row
        typesSet - the set of all different column types in existence to
                   be maintained
        """

        # Note: os path for the file we use must always exist as this is
        # always called after handleFileInput
        dynamicDB = {}
        # Load from a preexisting storage file.
        if self.type == '.bin':
            # Read from the file, line by line (row by row).
            if os.path.isfile(self.filename):
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
