import random
import string
import re
import ast
import SharedFunctions

""" Module: Insert
    Description: holds all information relating to inserts, including 
                 processing input
    Classes: Insert
"""


class Insert:
    """ Insert Class holds all information relating to inserts, including
    processing input.

    Variables:
    matches -- the passed in raw input from handleInput
    insertedRow -- the new row we add to the key value store
    typesSet -- the current set of all currently held column types

    Functions:
    generateRandomKey: Generates a random key if the user does not supply
                       one or the user supplied one exists in the store
    generateNewRows: Creates a new row/entry based on either a user supplied key
    handleInserts: parses matches to input used to insert a new row
    """

    def __init__(self, matches, typesSet):
        self.matches = matches
        self.insertedRow = {}
        self.typesSet = typesSet

    def generateRandomKey(self):
        """ generateRandomKey generates a random key to be used when inserting
        new values to the dictionary key value store.

        This is called if the user does not specify a key to insert with or if
        the key the user supplies is already in the key value store.

        No keyword arguments

        Return values:
        key -- a randomly generated key
        """

        key = 'row-' + ''.join(random.choices(string.ascii_lowercase +
                                              string.digits, k=4))
        key = key + ''.join(random.choices('!@#$%^&~_-.+', k=1))
        key = key + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        key = key + ''.join(random.choices('!@#$%^&~_-.+', k=1))
        key = key + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return key

    def generateNewRows(self, colValList):
        """ generateNewRows creates the new values to the dictionary key value
        store.

        Keyword Argument:
        colValList -- a list of the parameters for the new row

        Return values:
        newValues -- the inserted row (with a randomly generated key)
        """

        # check that all columns are valid
        newValues = {}
        if len(colValList) % 2 == 1:
            print("Column types must be associated with column values! "
                  "\n Usage:\n INSERT "
                  "[key] WITH "
                  "VALUES (col=tag, col2=tag2...) \n INSERT VALUES (col=tag,"
                  " col2=tag2, col3=tag3...)")
            return {}
        for i in range(0, len(colValList), 2):
            # Add the column type to typesSet if not in existence
            if colValList[i] not in self.typesSet:
                self.typesSet.add(colValList[i])
            # Check the type of the value type argument, and only convert to string
            # if it is not a string yet, and generate the new row.
            if type(colValList[i + 1]) != str:
                newValues[colValList[i]] = ast.literal_eval(str(colValList[i + 1]))
            else:
                newValues[colValList[i]] = str(colValList[i + 1])

        return newValues

    def handleInserts(self, dynamicDB):
        """ handleInserts returns a newly generated row to be inserted to the
        store.

        First, the function passes a set of matches generated using regex. If
        a key is in the store, then a message explaining this is printed out
        and a random key is generated instead.
        If the format is incorrect (not
        as INSERT [key] WITH VALUES (col=tag, col2=tag2, col3=tag3….),
        INSERT VALUES (col=tag, col2=tag2, col3=tag3…),
        a usage is printed out, and the current operation is abandoned.

        Keyword Arguments:
        dynamicDB -- the key value store maintained in the program

        Return values:
        self.insertedrow -- the row we are inserting
        """

        key = ''
        values = {}
        equalMatches = self.matches
        parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"]+', re.IGNORECASE)
        matches = parser.findall(" ".join(self.matches))
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
                    key = self.generateRandomKey()
            matches = SharedFunctions.spaceMatches(4, equalMatches)
            # This function parses the matches and generates new rows in the
            # proper format.
            values = self.generateNewRows(matches)
        # This is if the user inputs in the format
        # INSERT VALUES (col=tag, col2=tag2, col3=tag3…)
        elif matches[1].lower() == 'values' and len(matches) >= 3:
            matches = SharedFunctions.spaceMatches(2, equalMatches)
            while key in dynamicDB or key == '':
                key = self.generateRandomKey()
            values = self.generateNewRows(matches)
        else:
            print("Insert format is incorrect. Usage:\n INSERT [key] WITH "
                  "VALUES (col=tag, col2=tag2...) \n INSERT VALUES (col=tag,"
                  " col2=tag2, col3=tag3...)")
        if values != {}:
            self.insertedRow = {key: {'isFree': 'false', 'data': values}}
        return self.insertedRow
