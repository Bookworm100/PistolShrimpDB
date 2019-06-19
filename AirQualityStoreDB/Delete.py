import re
import SharedFunctions

""" Module: Delete
    Description: holds all information relating to deletes, including 
                 processing input
    Classes: Delete
"""


class Delete:
    """ Update Class holds all information relating to updates, including
       processing input.

       Variables:
       matches - the passed in raw input from handleInput
       selectedKeys - the list of keys to delete
       typesSet - the current set of all currently held column types

       Functions:
       handleDeletes: parses matches to input used to delete an existing row
                      (if the key and its value don't exist, we print an error
                      message instead).

       """

    def __init__(self, matches, typesSet):
        self.matches = matches
        self.selectedKeys = []
        self.typesSet = typesSet

    def handleDeletes(self, dynamicDB):
        """ handleDeletes handles all information relating to deletes, including
                 processing input.
        handleDeletes passes either a key or a set of values to the function
        marking keys for deletion. The matches generated using regex are used
        for this purpose. If a key is not in the store, then a message
        explaining this is printed out. If the format is incorrect (not
        as DELETE [key], or DELETE VALUES (col=tag, col2=tag2, col3=tag3….)
        a usage is printed out, and the current operation is abandoned.

        Keyword Arguments:
        dynamicDB - the key value store maintained in the program

        Return values:
        selectedKeys, the list of keys that we delete from the store. """

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
