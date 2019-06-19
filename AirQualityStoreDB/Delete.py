import re
from itertools import groupby
import SharedFunctions

class Delete:
    #def super(Insert, self).super()
    def __init__(self, matches, typesSet):
        self.matches = matches
        self.selectedKeys = []
        self.typesSet = typesSet

    """ handleDeletes passes either a key or a set of values to the function """
    """ marking keys for deletion. The matches generated using regex are used """
    """ for this purpose. If a key is not in the store, then a message """
    """ explaining this is printed out. If the format is incorrect (not """
    """ as DELETE [key], or DELETE VALUES (col=tag, col2=tag2, col3=tag3….) """
    """ a usage is printed out, and the current operation is abandoned. """
    """ @:param: matches, a list of strings of words """
    """ @:param: dynamicDB, the key value store maintained in the program """
    """ @:return: selectedKeys, the list of keys that we delete from the store. """

    def handleDeletes(self, dynamicDB):
        parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"]+', re.IGNORECASE)
        matches = parser.findall(" ".join(self.matches))
        # This is if the input is in the form DELETE VALUES (col=tag, col2=tag2...)
        if matches[1].lower() == 'values' and len(matches) >= 3:
            if "and" in " ".join(matches).lower() or "or" in " ".join(matches).lower():
                matches = SharedFunctions.conjMatches(2, self.matches)
                self.selectedKeys += SharedFunctions.selectKeyswithAndOrs(matches, dynamicDB)
            else:
                matches = SharedFunctions.spaceMatches(2, self.matches)
                self.selectedKeys += SharedFunctions.findMatchingKeys(matches, dynamicDB)
        # This is if just a key was specified.
        elif len(matches) == 2:
            if matches[1].lower() in dynamicDB and dynamicDB[matches[1].lower()] \
                    ['isFree'] == 'false':
                self.selectedKeys.append(matches[1].lower())
            else:
                print("The key is not in the store!")
        else:
            print("Delete format is incorrect. Usage:\n DELETE [key] "
                  " \n DELETE VALUES (col=tag,"
                  " col2=tag2, col3=tag3...)")
        return self.selectedKeys
