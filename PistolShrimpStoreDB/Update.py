import re
import json
import ast
import SharedFunctions

""" Module: Update
    Description: holds all information relating to updates, including 
                 processing input
    Classes: Update
"""

class Update:
    """ Update Class holds all information relating to updates, including
    processing input.

    Variables:
    matches - the passed in raw input from handleInput
    updatedRow - the new row we update its corresponding key with
    replacedRow - the row that was replaced (had its information updated)
    typesSet - the current set of all currently held column types

    Functions:
    handleUpdates: parses matches to input used to update an existing row
                   (if the key and its value don't exist, we print an error
                   message instead).

    """
    def __init__(self, matches, typesSet):
        self.matches = matches
        self.updatedRow = {}
        self.replacedRow = {}
        self.typesSet = typesSet

    def handleUpdates(self, dynamicDB):
        """ handleUpdates handles anything in the form UPDATE [key] WTIH VALUES
        (col=tag, col2=tag2, etc). Any other format causes the file to abandon
        the modification. Through each (col=tag, col2=tag2, etc), we change
        tag type's value to be the new value the user passed in. This set of
        changed values is then set to be the data with the value associated
        with the key. Other irregularities causing abandonment of modification
        include the type not being in the set of accepted types, and having
        tags/values without the other.
        dynamicDB - the key value store maintained in the program
        self.updatedRow, self.replacedRow - the tuple of a new row to update
                                            with, and the row to be replaced
        """
        error = False
        usage = "Usage:\n UPDATE [key] WITH  VALUES (col=tag, col2=tag2...) \n"
        parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"]+', re.IGNORECASE)
        matches = parser.findall(" ".join(self.matches))
        if matches[2].lower() == 'with' and matches[3].lower() == 'values' \
                and len(matches) >= 5:
            # check if key already exists in the key value store
            key = matches[1].lower()
            if key in dynamicDB and dynamicDB[key]['isFree'] == 'false':
                allVals = dynamicDB[key]['data']
                replaced = json.dumps(dynamicDB[key]['data'])
                matches = SharedFunctions.spaceMatches(4, self.matches)
                # Check that all types/columns are matched correctly
                if len(matches) % 2 == 1:
                    print("Column types must be associated with column values!"
                          " \n ", usage)
                    error = True
                # Check that either the column we want to modify
                # is in the row or is in the set. Otherwise,
                # this is an invalid input.
                if not error:
                    for colIndex in range(0, len(matches), 2):
                        if matches[colIndex] not in self.typesSet:
                            self.typesSet.add(matches[colIndex])
                        allVals[matches[colIndex]] = matches[colIndex + 1]
                    # Now set the data of the row to be the modified values.
                    dynamicDB[key]['data'] = allVals
                    self.updatedRow = {key: {'isFree': 'false', 'data': allVals}}
                    self.replacedRow = {key: {'isFree': 'false', 'data':
                                         ast.literal_eval(replaced)}}
            else:
                print("The key is not in the store!")
        else:
            print("UPDATE format is incorrect. \n", usage)
        return self.updatedRow, self.replacedRow
