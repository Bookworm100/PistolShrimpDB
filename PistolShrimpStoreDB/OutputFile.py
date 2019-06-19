import sys

""" Module: OutputFile
    Description: OutputFile.py contains functions specifically to write to 
                 the intended storage file.

    Functions: 

        saveChanges - saves changes made to the running key value store

        updateFileWithUpdates - saves all updates to the storage file

        updateFileWithDeletes - saves all deletions to the storage file
        
        updateFileWithInserts - saves all insertions ot the storage file
"""

# Note: all global variables will not be modified
# size of blocks of memory in bytes
blockSize = 1000


def saveChanges(isNewDBFile, storageDBFile, dynamicDB,
                deletedKeys, insertedRows, updatedRows,
                maximumPosition):
    """ saveChanges saves the currently running key value store
    to the storage file (which will be created if necessary).

     The indices of the deleted keys are stored in a list, which
     are then passed to updateFileWithDeletes to delete from
     the storage file. Next, for every "key" that was updated,
     the index of the key (from the list of keys
     obtained from the dictionary), the key itself, and its value
     are stored in a list, which is used to update the corresponding line in
     the storage file, and finally, the list of inserted rows is passed to
     the updateFileWithInserts, where the information is written to the
     end of the file.

     Keyword Arguments:
     isnewDBFile - a boolean indicating if the file is new
     storageDBFile - the name of the file storing the rows
     dynamicDB - the key value store maintained in the program
     deletedKeys - the list of keys deleted from the store
     insertedRows - the list of inserted rows
     updatedRows - the list of updated rows

     No return values
     """

    # Once the key value store is to be closed, we save any changes.
    # If the key value store file didn't exist yet, then
    # a new one is created here.
    c = 0
    if isNewDBFile:
        with open(storageDBFile, 'wb') as file:
            for item in dynamicDB:
                if 'position' not in dynamicDB[item]:
                    continue
                toWrite = '{' + json.dumps(item) + ': ' + \
                              json.dumps(dynamicDB[item]) + '}' + '\n'
                toByte = toWrite.encode('utf-8')
                file.write(('\0' * (blockSize - sys.getsizeof(toByte)))
                               .encode('utf-8'))
                file.write(toByte)
                c += 1
        maximumPosition = c - 1

    keyList = list(dynamicDB.keys())
    indicesToDelete = []
    updateInfo = []
    for each in deletedKeys:
        # The position is a marker if the item was loaded from the
        # file. If the item was not loaded from the file
        # and is being deleted, then we cannot delete it
        # from the storage file
        if 'position' in dynamicDB[each]:
            indicesToDelete.append(keyList.index(each))
        else:
            # Otherwise, we were originally going to insert
            # this value, so we want to make sure that this
            # is not written to the file.
            del insertedRows[each]

    # We need the index for each row so we know which lines to modify.
    for each in updatedRows:
        updateInfo.append((keyList.index(each), each, dynamicDB[each]))

    if len(updateInfo) > 0:
        updateFileWithUpdates(storageDBFile, updateInfo)
    if len(indicesToDelete) > 0:
        updateFileWithDeletes(storageDBFile, indicesToDelete)
    if len(insertedRows) > 0:
        maximumPosition = updateFileWithInserts(storageDBFile, insertedRows, maximumPosition)
    return maximumPosition


def updateFileWithUpdates(storageDbFile, updatedRows):
    """ updateFileWithUpdates modifies the value store from the storage file.

    As Python 3.6+ preserves order
    in dictionaries, it's possible to recall the positions of keys (in the
     storage file) to be updated by
    using simple Python function calls (handled in the main function).
    The list of these indices is the argument. As the key did not change,
     the positions that changed are passed in as a list with its associated
     key and row and then using read lines, we modifiy only the lines
     we want and then write them back to the file.

     storageDBFile - the name of the file storing the rows
     updatedRows - the list of line information of rows to update.
              Each tuple includes the line indices and the new information
              to write, including the key and new information.
     No return values
     """

    # We can write back
    # We read each line currently in the storage file
    # as a separate element in a list.
    with open(storageDbFile, 'rb+') as open_file:
        for tup in updatedRows:
            toWrite1 = '{' + json.dumps(tup[1]) + ': ' + \
                       json.dumps(tup[2]) + '}' + '\n'
            # We encode the key-value pair in binary and
            # write to file.
            toByte1 = toWrite1.encode('utf-8')
            toWrite2 = ('\0' * (blockSize - sys.getsizeof(toByte1)))
            toByte2 = toWrite2.encode('utf-8')
            line = toByte2 + toByte1
            sizeOfLine = len(line)
            open_file.seek((tup[0]) * sizeOfLine)
            open_file.write(line)


def updateFileWithDeletes(storageDbFile, indicesDeleted):
    """ updateFileWithDeletes removes items marked for deletion in the key
    value store from the storage file.

    As Python 3.6+ preserves order
     in dictionaries, it's possible to recall the positions of keys (in the
     storage file) to be deleted by
     using simple Python function calls (handled in the main function).
     The list of these indices is the argument.

     Keyword Arguments:
     storageDBFile - the name of the file storing the rows
     indicesDeleted - the list of line indices to delete.

     No return values
     """

    # We read each line currently in the storage file
    # as a separate element in a list.
    indList = sorted(indicesDeleted, reverse=True)
    lenLine = 0
    with open(storageDbFile, 'r+b') as open_file:
        line = open_file.readline()
        lenLine = len(line)
        open_file.seek(indicesDeleted[0] * lenLine)
        lineList = open_file.readlines()
    # We sort the indices in reverse, and remove
    # the value (and line) corresponding to each index in the
    # storage file.
    for index in indList:
        del lineList[index - indicesDeleted[0]]
    # We write the modified lines back to the file.
    with open(storageDbFile, 'rb+') as open_file:
        open_file.seek(indicesDeleted[0] * lenLine)
        open_file.writelines(lineList)
        open_file.truncate()


def updateFileWithInserts(storageDbFile, insertedRows, maximumPosition):
    """ In updateFileWithInserts,
     We are appending to the end of the file, as all rows to be deleted
     have been deleted.

     We write a new row corresponding to each value we
     insert. The format of writing should be similar to the method of first
     writing in the lines in the first place.
     storageDBFile - the name of the file storing the rows
     insertedRows - the list of rows to insert to the file
     maximumPosition - the final position in the file, incremented
             with each inserted row

     No return values
     """
    with open(storageDbFile, 'a+b') as file1:
        for item1 in insertedRows:
            maximumPosition += 1
            insertedRows[item1]['position'] = maximumPosition
            toWrite1 = '{' + json.dumps(item1) + ': ' + \
                       json.dumps(insertedRows[item1]) + '}' + '\n'
            # We encode the key-value pair in binary and
            # write to file.
            toByte1 = toWrite1.encode('utf-8')
            file1.write(('\0'*(blockSize-sys.getsizeof(toByte1)))
                        .encode('utf-8'))
            file1.write(toByte1)
    return maximumPosition
