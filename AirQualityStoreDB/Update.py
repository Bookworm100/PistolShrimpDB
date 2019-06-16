import re
import json
import ast
import SharedFunctions

class Update:
    #def super(Insert, self).super()
    def __init__(self, matches, typesSet):
        self.matches = matches
        self.updatedRow = {}
        self.replacedRow = {}
        self.typesSet = typesSet

    """ handleUpdates handles anything in the form UPDATE [key] WTIH VALUES """
    """ (col=tag, col2=tag2, etc). Any other format causes the file to abandon """
    """ the modification. Through each (col=tag, col2=tag2, etc), we change """
    """ tag type's value to be the new value the user passed in. This set of """
    """ changed values is then set to be the data with the value associated """
    """ with the key. Other irregularities causing abandonment of modification """
    """ include the type not being in the set of accepted types, and having """
    """ tags/values without the other. """
    """ @:param: matches, a list of strings of words """
    """ @:param: dynamicDB, the key value store maintained in the program """
    """ @:return: newOldRows, the tuple of a new row to update with, and the row """
    """           to be replaced """

    def handleUpdates(self, dynamicDB):
        newOldRows = ()
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

                        #else:
                        #    print(matches[colIndex], " is an invalid column type! \n "
                        #          , usage)
                        #    error = True
                    # Now set the data of the row to be the modified values.
                    dynamicDB[key]['data'] = allVals
                    self.updatedRow = {key: {'isFree': 'false', 'data': allVals}}
                    self.replacedRow = {key: {'isFree': 'false', 'data':
                                         ast.literal_eval(replaced)}}
            else:
                print("The key is not in the store!")
                error = True
        else:
            print("UPDATE format is incorrect. \n", usage)
            error = True
        return self.updatedRow, self.replacedRow
