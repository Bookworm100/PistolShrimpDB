# Import statements:
# The documents we're using require JSON
import os.path
import sys
import re
from InputFile import inputFile
from Insert import Insert
from Delete import Delete
from Update import Update
import OutputFile
import Selects
import Search

""" Module: Main 
    Description: Main.py is the main engine of this key value store.

    Class:
        renamed - a renamed class storing a tuple of a renamed column
                  the name that that column type now bears.
        
        PistolShrimpStore - the class that represents the key value store and
                            other variables necessary to keep the value store
                            inserting, deleting, updating, selecting, searching,
                            and finding correctly.

    Functions: 

        handleFileInput - The user is asked to specify a file to load the data
                          from, and then places to load the data and columns
                          (which is always optional).
        
        main - Runs the main engine by calling handleFileInput, then creates
               the instances of InputFile and PistolShrimpStore, which handles 
               nearly all the following work.
               
        
        
"""


class renamed:
    """ A tuple of the original and new names of a specific column.

    Variables:
    original - the original name
    new - the new name of the renamed column
    """

    def __init__(self, col1, col2):
        self.original = col1
        self.new = col2

class pistolShrimpStore:
    """ pistolShrimpStore represents the key value store and everything necessary
        to keep the value store inserting, deleting, updating, selecting,
        searching, and finding correctly.

       Variables:
       dynamicDB - the key value store that is all the fuss
       storageFile - the storage file that will be written to
       insertedRows - the maintained dictionary of every insertedRow
                      since the last save/undo or opening of the program
       deletedKeys - the list of every deleted key since the last save/undo or
                     opening of the program
       updatedRows - the dictionary of every updated row since the last
                     save/undo or opening of the program
       replacedRows - the dictionary of replacedRow objects since the last
                      save/undo or opening of the program (from update)
       renamedColumns - the list of renamed column objects with the original
                        and renamed names
       maximumPosition - the maintained maximum position used to write to the
                         storage file when adding inserting rows.
       isNewDBFile - the flag indicating if this is a new dbfile
       typesSet - the set of column types currently in existence

       Functions:
       handleInput: passes the input to instaances of Update, Delete, Insert,
                    Search, and Select
       reset: resets the values of insertedRows, deletedKeys, updatedRows,
              replacedRows, and renamedColumns after a save/undo.
       invokeUndo: Reverts all changes to dynamicDB since the last save/undo or
                   opening of the file, and then calls reset
       invokeSave: Saves all changes to dynamicDB to the storage file since the
                   last save/undo or opening of the file, and then calls reset
       handleRenamed: renames all the columns in dynamicDB and saves the
                      renamedObject in case of undo.
       run: The main program function of the file, and invokes input, and
            handles any action (such as to turn the input to handleInputs
            or to exit the program)


    """

    def __init__(self, storageFile, dynamicDB, isNewDBFile, maximumPosition,
                 typesSet):
        self.dynamicDB = dynamicDB
        self.storageFile = storageFile
        self.insertedRows = {}
        self.deletedKeys = []
        self.updatedRows = {}
        self.replacedRows = {}
        self.renamedColumns = []
        self.isNewDBFile = isNewDBFile
        self.maximumPosition = maximumPosition
        self.typesSet = set(typesSet)

    def handleInput(self, command):
        """ handleInput will be used to execute commands to change the key value
        store.

        This handles insertions, deletions, select statements,
        update statements, search/find statements, and rename statements.
        Insert commands will return the new rows, Delete statements returns a
        list of keys of deleted items, Update statements return updated rows,
        rename statements return rename objects of tuples, and
        SELECT, SEARCH, and FIND STATEMENTS will print the outputs
        while also returning nothing.

        Keyword Argument:
        command, the raw command passed in by the user

        Return values:
         changesMade - an object of type Insert, Delete, Update, Rename,
         or None depending on which command the input was to execute.
         The object will be used to update dynamicDB and any variables
         used to keep track of changes for save/undo purposes.
         """

        # check the inputs
        parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+={}():\'",]+', re.IGNORECASE)
        matches = parser.findall(command)
        changesMade = None
        if matches[0].lower() == 'insert':
            changesMade = Insert(matches, self.typesSet)
        elif matches[0].lower() == 'rename':
            changesMade = renamed(matches[1].lower(), matches[2].lower())
        elif matches[0].lower() == 'delete':
            changesMade = Delete(matches, self.typesSet)
        elif matches[0].lower() == 'update':
            changesMade = Update(matches, self.typesSet)
        elif matches[0].lower() == 'select':
            Selects.handleSelects(matches, self.dynamicDB)
        elif matches[0].lower() == 'search':
            Search.handleSearches(matches, self.dynamicDB)
        elif matches[0].lower() == 'find':
            Search.handleSearches(matches, self.dynamicDB, True)
        return changesMade

    def reset(self):
        """resets the values of insertedRows, deletedKeys, updatedRows,
              replacedRows, and renamedColumns after a save/undo.
        No Keyword Arguments or return values
        """

        # The applicable changes have been saved to the
        # storage file, so we no longer need them.
        self.insertedRows.clear()
        self.deletedKeys.clear()
        self.updatedRows.clear()
        self.replacedRows.clear()
        self.renamedColumns.clear()


    def invokeUndo(self):
        """Reverts any changes made to dynamicDB since the last save/undo
           or loading of the program.
           No Keyword Arguments or return values
        """

        # Delete any added row
        for each in self.insertedRows:
            del self.dynamicDB[each]

        # Reset 'isFree' of deleted rows
        for each in self.deletedKeys:
            self.dynamicDB[each]['isFree'] = 'false'

        # Restore replaced rows
        for each in self.replacedRows:
            self.dynamicDB[each] = self.replacedRows[each]

        # Revert renaming of columns
        for each in self.dynamicDB:
            for tup in self.renamedColumns:
                col2, col1 = tup
                reassigned = self.dynamicDB[each]['data'][col1]
                del self.dynamicDB[each]['data'][col1]
                self.dynamicDB[each]['data'][col2] = reassigned

        print("Successfully undoed ", len(self.insertedRows),
              " insertions, ", len(self.deletedKeys), " deletions, and ",
              len(self.updatedRows), " updates!", "\n")

    def invokeSave(self):
        """ saves all changes to dynamicDB.

        No Keyword Arguments or return values
        """
        # TODO: Test this
        # Add renamed values to updated rows
        for item in self.dynamicDB:
            for tup in self.renamedColumns:
                if tup.original in self.dynamicDB[item]:
                    self.updatedRows.update(self.dynamicDB[item])

        # Save all updates (replacemed columns go here), deletes, and insertions
        self.maximumPosition = OutputFile.\
                               saveChanges(self.isNewDBFile, self.storageFile,
                                           self.dynamicDB, self.deletedKeys,
                                           self.insertedRows, self.updatedRows,
                                           self.maximumPosition)
        # Get rid of deleted keys
        for each in self.deletedKeys:
            del self.dynamicDB[each]
        print("Successfully saved ", len(self.insertedRows), " insertions, "
              , len(self.deletedKeys), " deletions, and ",
              len(self.updatedRows), " updates!", "\n")

    def handleRenamed(self, handleValue):
        # TODO: Finish documentation for handleRenamed and Main
        """
        """
        col1 = handleValue.original
        col2 = handleValue.new
        tup = (col1, col2)
        counter = 0
        for each in self.dynamicDB:
            if col1 in self.dynamicDB[each]['data']:
                counter += 1
                reassigned = self.dynamicDB[each]['data'][col1]
                del self.dynamicDB[each]['data'][col1]
                self.dynamicDB[each]['data'][col2] = reassigned
        if counter == 0:
            print("The first column you specified does not exist! Please "
                  "note the syntax is RENAME col1 col2, where col1 is the"
                  "original column and col2 is the column name that is what"
                  " you want col1 to be replaced with.")
        else:
            self.renamedColumns.append(tup)
            print("Successfully renamed ", col1, " as ", col2,"!")

    def run(self):
        # This section handles user input and passes it to
        # the handleInput function to change the key value
        # store.
        toSave = True
        while True:
            n = input("Now we can do awesome stuff! You can exit the program "
                      "with exit or quit if you"
                      " want your changes saved, or with abort if you don't. "
                      "You can also save your changes with save and undo"
                      " them with undo! \n")

            if n == "quit" or n == "abort" or n == "exit":
                if n == "abort":
                    toSave = False
                break
            if len(n) == 0:
                continue
            # save and undo go here
            if n == "save":
                self.invokeSave()
                self.reset()
                self.isNewDBFile = False
                continue
            elif n == "undo":
                # Do stuff
                self.invokeUndo()
                self.reset()
                continue
            else:
                handleValue = self.handleInput(n)

                # check the class
                if handleValue is not None:
                    if type(handleValue) == renamed:
                        self.handleRenamed(handleValue)
                    elif type(handleValue) == Insert:
                        newRow = handleValue.handleInserts(self.dynamicDB)
                        self.insertedRows.update(newRow)
                        self.dynamicDB.update(newRow)
                        for key in newRow:
                            print("Successfully inserted ", key, ": ",
                                  newRow[key]['data'], "\n")
                    elif type(handleValue) == Delete:
                        row = handleValue.handleDeletes(self.dynamicDB)
                        for item in row:
                            self.dynamicDB[item]['isFree'] = 'true'
                            # This is in the storage file, so
                            # we should erase them.
                            if 'position' in self.dynamicDB[item]:
                                self.deletedKeys.append(item)
                            else:
                                # This was a new row, so we do not
                                # want to write this to the file.
                                del self.insertedRows[item]
                            # If there were rows updated, we
                            # want to make sure these aren't
                            # written to the file because they
                            # were deleted.
                            if item in self.updatedRows:
                                del self.updatedRows[item]
                            print("Successfully deleted ", item, ": ",
                                  self.dynamicDB[item]['data'], "\n")
                    elif type(handleValue) == Update:
                        updatedRow, replacedRow = handleValue.handleUpdates(self.dynamicDB)
                        if updatedRow is not None and len(updatedRow) > 0:
                            for key in updatedRow:
                                # If this is a new row (inserted after loading the
                                # storage
                                # file), then we simply change the inserted value.
                                if key in self.insertedRows:
                                    self.insertedRows[key] = updatedRow[key]
                                else:
                                    self.updatedRows.update(updatedRow)
                                    if key not in self.replacedRows:
                                        self.replacedRows.update(replacedRow)
                                print("Successfully updated ", key, ": ",
                                      self.dynamicDB[key]['data'], "\n")

        if toSave:
            OutputFile.saveChanges(self.isNewDBFile, self.storageFile, self.dynamicDB,
                      self.deletedKeys, self.insertedRows, self.updatedRows,
                      self.maximumPosition)





"""Here: the filename is specified, as is the column types to search for, """
""" and where to find the data. """
def handleFileInput():
    # Let the user specify which file to use
    toLoadFile = input("Welcome to PistolShrimpDB! If you would like to specify "
                       "a file to load from, type it here else, hit enter."
                       " If our default storage file does not exist yet,  "
                       "you must specify the file."
                       "\n")

    print("Loading...\n")
    if len(toLoadFile) == 0:
        toLoadFile = "PistolShrimpDB.bin"

    while not os.path.isfile(toLoadFile):
        toLoadFile = input("We're sorry! This file does not seem to exist " +
                            "or you did not specify a file when the storage"
                            "file has not been created yet. "
                           "Please type in a valid file name and/or path. " +
                           "\n")

    whereKey = input("If you would like to specify where the key or column "
                     "types are, type it here, else, hit enter."
                     "\n")

    whereData = input("If you would like to specify the keyword where the "
                      "data is, type it here, else, hit enter."
                      "\n")

    if len(whereKey) == 0:
        whereKey = "columns"
    if len(whereData) == 0:
        whereData = "data"
    return toLoadFile, whereKey, whereData


""" The main function checks if a file exists that contains the key value """
""" store, and if it does, then we load the store from the file. Otherwise, """
""" one is initialized from a JSON file (as the store is configured around """
""" a specific JSON file storing air quality measurements. This main """
""" function will ideally hold handling user input and other operations """
""" necessary, and when the key value store is closed, any changes are """
""" written to the file which stores the key value store. Note: """
""" This only works in Python 3.6+. Otherwise, we would """
""" need to use something like orderedDict. """
""" @params: none """
""" @return: none """
if __name__ == "__main__":
    # This program will only work properly
    # with Python versions 3.6+, so we check that
    # the version is infact 3.6+
    assert sys.version_info >= (3, 6)

    # Create new file instance
    inputFileInstance = inputFile(*handleFileInput())

    initialDB, toCreateDBFile, maxPosition, setOfTypes \
        = inputFileInstance.loadFile()

    DBFile = input("If you would like to specify "
                   "a file to write to, type it here else, hit enter."
                   "\n")
    if len(DBFile) == 0:
        DBFile = 'PistolStorageDB.bin'

    pSStore = pistolShrimpStore(DBFile, initialDB, toCreateDBFile, maxPosition,
                                setOfTypes)

    pSStore.run()

    print("Goodbye! Hope to see you again soon!")