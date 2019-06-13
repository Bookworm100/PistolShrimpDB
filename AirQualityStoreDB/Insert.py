import random
import string
import re
import ast

class Insert:
    #def super(Insert, self).super()
    def __init__(self, matches, typesSet):
        self.matches = matches
        self.insertedRow = {}
        self.typesSet = typesSet


    """ generateRandomKey generates a random key to be used when inserting new """
    """ values to the dictionary key value store. """
    """ @:param: None """
    """ @:return: key, a randomly generated key """

    def generateRandomKey(self):
        key = 'row-' + ''.join(random.choices(string.ascii_lowercase +
                                              string.digits, k=4))
        key = key + ''.join(random.choices('!@#$%^&~_-.+', k=1))
        key = key + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        key = key + ''.join(random.choices('!@#$%^&~_-.+', k=1))
        key = key + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return key


    """ generateNewRows will insert the new values to the dictionary key value """
    """ store, and keep track of what should get added to the storage file """
    """ upon exiting or quitting. """
    """ @:param: colValList, a list of the parameters for the new row """
    """ @:return: newValues, the inserted row (with a randomly generated key) """

    def generateNewRows(self, colValList):
        # check that all columns are valid, and build up a dictionary.
        # By looping through every pair, and
        newValues = {}
        if len(colValList) % 2 == 1:
            print("Column types must be associated with column values! "
                  "\n Usage:\n INSERT "
                  "[key] WITH "
                  "VALUES (col=tag, col2=tag2...) \n INSERT VALUES (col=tag,"
                  " col2=tag2, col3=tag3...)")
            return {}
        for i in range(0, len(colValList), 2):
            if colValList[i] not in self.typesSet:
                self.typesSet.add(colValList[i])

            newValues[colValList[i]] = ast.literal_eval(str(colValList[i + 1]))

        return newValues


    """ handleInserts passes a set of matches generated using regex. """
    """ If a key is in the store, then a message """
    """ explaining this is printed out and a random key is generated instead."""
    """ If the format is incorrect (not """
    """ as INSERT [key] WITH VALUES (col=tag, col2=tag2, col3=tag3….), """
    """ INSERT VALUES (col=tag, col2=tag2, col3=tag3…), """
    """ a usage is printed out, and the current operation is abandoned. """
    """ @:param: matches, a list of strings of words """
    """ @:param: dynamicDB, the key value store maintained in the program """
    """ @:return: row, the row we just inserted """

    def handleInserts(self, dynamicDB):
        key = ''
        values = {}
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
            matches = matches[4:]
            # This function parses the matches and generates new rows in the
            # proper format.
            values = self.generateNewRows(matches)
        # This is if the user inputs in the format
        # INSERT VALUES (col=tag, col2=tag2, col3=tag3…)
        elif matches[1].lower() == 'values' and len(matches) >= 3:
            matches = matches[2:]
            while key in dynamicDB or key == '':
                key = self.generateRandomKey()
            values = self.generateNewRows(matches)
        else:
            print("Insert format is incorrect. Usage:\n INSERT [key] WITH "
                  "VALUES (col=tag, col2=tag2...) \n INSERT VALUES (col=tag,"
                  " col2=tag2, col3=tag3...)")
            # row = {}
        if values != {}:
            self.insertedRow = {key: {'isFree': 'false', 'data': values}}
        return self.insertedRow




