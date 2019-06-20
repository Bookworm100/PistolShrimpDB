# Import statements:
# The documents we're using require JSON
import os.path
import sys
import re
import json
import ast
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
                          
        specifyOutputFile - determines the output file to write to, and gives
                            the option to specify an output file
        
        main - Runs the main engine by calling handleFileInput, then creates
               the instances of InputFile and PistolShrimpStore, which handles 
               nearly all the following work.
"""


class renamed:
    """ A tuple of the original and new names of a specific column.

    Variables:
    original -- the original name
    new -- the new name of the renamed column
    """

    def __init__(self, All):
        All = " ".join(All)
        parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+={}():",\s]+', re.IGNORECASE)
        matches = parser.findall(All)
        if len(matches) < 2 or (len(matches) > 3
                                or (len(matches) == 3 and matches[1] != ' ')):
            print("There should only be two columns! Please "
                  "note the syntax is RENAME col1 col2, where col1 is the"
                  " original column and col2 is the column name that is what"
                  " you want col1 to be replaced with.")
            self.original = None
            self.new = None
            return
        col1 = matches[0]
        if len(matches) == 2:
            col2 = matches[1]
        else:
            col2 = matches[2]
        if '\'' in col1:
            col1 = col1[1:-1]
        if '\'' in col2:
            col2 = col2[1:-1]
        self.original = col1
        self.new = col2

class pistolShrimpStore:
    """ pistolShrimpStore represents the key value store and everything necessary
    to keep the value store inserting, deleting, updating, selecting,
    searching, and finding correctly.

    Variables:
    dynamicDB -- the key value store that is all the fuss
    storageFile -- the storage file that will be written to
    insertedRows -- the maintained dictionary of every insertedRow
                    since the last save/undo or opening of the program
    deletedKeys -- the list of every deleted key since the last save/undo or
                   opening of the program
    updatedRows -- the dictionary of every updated row since the last
                   save/undo or opening of the program
    replacedRows -- the dictionary of replacedRow objects since the last
                    save/undo or opening of the program (from update)
    renamedColumns -- the list of renamed column objects with the original
                      and renamed names
    maximumPosition -- the maintained maximum position used to write to the
                       storage file when adding inserting rows.
    isNewDBFile -- the flag indicating if this is a new dbfile
    typesSet -- the set of column types currently in existence

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
        command -- the raw command passed in by the user

        Return values:
        changesMade -- an object of type Insert, Delete, Update, Rename,
                       or None depending on which command the input was to
                       execute. The object will be used to update dynamicDB and
                       any variables used to keep track of changes for
                       save/undo purposes.
        """

        # check the inputs
        parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+={}():\'",]+', re.IGNORECASE)
        matches = parser.findall(command)
        changesMade = None
        if matches[0].lower() == 'insert':
            changesMade = Insert(matches, self.typesSet)
        elif matches[0].lower() == 'rename':
            changesMade = renamed(matches[1:])
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
        """ Resets the values of insertedRows, deletedKeys, updatedRows,
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
        """ Reverts any changes made to dynamicDB since the last save/undo
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

        print("Successfully undoed ", len(self.insertedRows),
              " insertions, ", len(self.deletedKeys), " deletions, and ",
              len(self.updatedRows), " updates!", "\n")

    def invokeSave(self):
        """ saves all changes to dynamicDB.

        No Keyword Arguments or return values
        """

        # Save all updates (replaced columns go here), deletes, and insertions
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
        """ handleRenamed renames a column, basically replacing a column name
        for every single row. A tuple representing the renamed object is
        added to a list of renamed columns, for the purposes of save/undo.

        Keyword Arguments:
        handleValue - the renamed object we will use for renaming

        No return values
        """

        col1 = handleValue.original
        col2 = handleValue.new
        tup = (col1, col2)
        counter = 0
        # For each item in the key value store, if the original column name
        # is in the item, then we rename that column by deleting that entry
        # and then rewriting that entry with the new name.
        for each in self.dynamicDB:
            if col1 in self.dynamicDB[each]['data'] and \
                      self.dynamicDB[each]['isFree'] == 'false':
                counter += 1
                oldRow = json.dumps(self.dynamicDB[each])
                reassigned = self.dynamicDB[each]['data'][col1]
                del self.dynamicDB[each]['data'][col1]
                self.dynamicDB[each]['data'][col2] = reassigned
                if each in self.insertedRows:
                    self.insertedRows[each]['data'][col2] = reassigned
                else:
                    self.updatedRows.update({each: self.dynamicDB[each]})
                    if each not in self.replacedRows:
                        self.replacedRows.update({each:
                                         ast.literal_eval(oldRow)})
        # The following only occurs if the original column name is
        # not in the store
        if counter == 0:
            print("The first column you specified does not exist! Please "
                  "note the syntax is RENAME col1 col2, where col1 is the"
                  " original column and col2 is the column name that is what"
                  " you want col1 to be replaced with.")
        else:
            self.renamedColumns.append(tup)
            print("Successfully renamed ", col1, " as ", col2,"!")

    def run(self):
        """ run is the main function managing the key value store.

        When called, it takes in user input, which it uses to exit the program,
        save, or undo the changes made. run also handles the modifications to
        the key value store itself as run is where the changes from insert,
        delete, and update are made to the running key store. Additionally, the
        variables necessary to allow for saving and undoing changes are
        maintained here. Finally, if the program is exited with exit or quit
        changes are saved to file.

        No keyword arguments or return value.
        """

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
            # Handle exiting the program here
            if n == "quit" or n == "abort" or n == "exit":
                if n == "abort":
                    toSave = False
                break
            if len(n) == 0:
                continue
            # Handle saving and undoing changes here
            if n == "save":
                self.invokeSave()
                self.reset()
                self.isNewDBFile = False
                continue
            elif n == "undo":
                self.invokeUndo()
                self.reset()
                continue
            else:
                # handle input here
                handleValue = self.handleInput(n)

                # Check the type of return value. If the value is of type
                # None, the key value store is to be updated. The actual
                # renaming, insertion, deletion, and updating happens here.
                if handleValue is not None:
                    if type(handleValue) == renamed:
                        if handleValue.original is not None:
                            self.handleRenamed(handleValue)
                    elif type(handleValue) == Insert:
                        newRow = handleValue.handleInserts(self.dynamicDB)
                        # We keep track of all row that have been inserted since
                        # the last save/undo or loading the program to either
                        # write them to the file or to reverse these changes.
                        self.insertedRows.update(newRow)
                        self.dynamicDB.update(newRow)
                        for key in newRow:
                            print("Successfully inserted ", key, ": ",
                                  newRow[key]['data'], "\n")
                    elif type(handleValue) == Delete:
                        row = handleValue.handleDeletes(self.dynamicDB)
                        for item in row:
                            self.dynamicDB[item]['isFree'] = 'true'
                            # These are in the storage file, so
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
                                # If this is a new row (inserted after loading
                                # the storage file), then we simply change the
                                # inserted value.
                                if key in self.insertedRows:
                                    self.insertedRows[key] = updatedRow[key]
                                else:
                                    self.updatedRows.update(updatedRow)
                                    if key not in self.replacedRows:
                                        self.replacedRows.update(replacedRow)
                                print("Successfully updated ", key, ": ",
                                      self.dynamicDB[key]['data'], "\n")
        # If the user specified to exit or quit, we save the changes. We don't
        # use invokeSave() as that involves unnecessary updating.
        if toSave:
            OutputFile.saveChanges(self.isNewDBFile, self.storageFile, self.dynamicDB,
                      self.deletedKeys, self.insertedRows, self.updatedRows,
                      self.maximumPosition)


def specifyOutputFile():
    """ specifyOutputFile determines the output file to write to.
    Until we know that a selected file is valid, we keep prompting the
    user to either specify an output file or to use the default version.

    No keyword arguments

    Return values:
    DBFile -- the name of the output file to use
    """

    DBFile = input("If you would like to specify "
                   "a file to write to, type it here, else, hit enter."
                   "\n")

    # Make sure the output file is valid.
    read = False
    while not read:
        try:
            if len(DBFile) == 0:
                DBFile = 'PistolShrimpStoreDB.bin'
            with open(DBFile, 'w') as file:
                read = True
        except IOError:
            # In the case the file cannot be created, the user is
            # asked if they changed their mind and want to use the
            # default file instead.
            DBFile = input("Sorry, this path seems to be invalid."
                           " Would you still like to create a custom file? "
                           " Again, type its name here, else, hit enter.\n")

    return DBFile


def handleFileInput():
    """ This function asks for and processes user input of file types and
    data/column information keywords.

    The filename is specified, as is the column types to search for,
    and where to find the data.

    No keyword arguments

    Return values:
    toLoadFile -- the file to load data from
    whereKey -- a keyword specifying where to possibly find column information
    whereData -- a keyword specifying where to possibly find data
    """

    # Let the user specify which file to use
    toLoadFile = input("Welcome to PistolShrimpDB! If you would like to specify "
                       "a file to load from, type it here else, hit enter."
                       " If our default storage file does not exist yet,  "
                       "you must specify the file."
                       "\n")

    print("Loading...\n")
    if len(toLoadFile) == 0:
        toLoadFile = "PistolShrimpStoreDB.bin"

    while not os.path.isfile(toLoadFile):
        toLoadFile = input("We're sorry! This file does not seem to exist " +
                           "or you did not specify a file when the storage"
                           "file has not been created yet. "
                           "Please type in a valid file name and/or path. " +
                           "\n")

    # Ask the user if they wish to specify where in the file to find
    # data or column information.
    whereKey = input("If you would like to specify where the key or column "
                     "types are, type it here, else, hit enter."
                     "\n")

    whereData = input("If you would like to specify the keyword where the "
                      "data is, type it here, else, hit enter."
                      "\n")

    # Set default values if they don't specify.
    if len(whereKey) == 0:
        whereKey = "columns"
    if len(whereData) == 0:
        whereData = "data"

    return toLoadFile, whereKey, whereData


if __name__ == "__main__":
    """ The main function checks the Python version and exits if the Python
    version is too old. We then create a new instance of InputFile, with our
    constructor arguments being the outputs of handleFileInput, which asks the
    user to specify a file to load from, as well as where to find data and
    column infomation. Once the file is loaded, we ask the user to specify an
    output file. Finally, we set up an instance of pistolShrimpStore, which
    is used for all the remaining work.
    Note: This only works in Python 3.6+. Otherwise, we would need to use
    something like orderedDict for the key value store.
    
    No keyword arguments or return values 
    """

    # This program will only work properly
    # with Python versions 3.6+, so we check that
    # the version is infact 3.6+
    assert sys.version_info >= (3, 6)

    # Create new file instance
    inputFileInstance = inputFile(*handleFileInput())

    initialDB, toCreateDBFile, maxPosition, setOfTypes \
        = inputFileInstance.loadFile()

    DBFile = specifyOutputFile()

    pSStore = pistolShrimpStore(DBFile, initialDB, toCreateDBFile
                                or (DBFile == inputFileInstance.filename),
                                maxPosition, setOfTypes)

    pSStore.run()

    print("Goodbye! Hope to see you again soon!")