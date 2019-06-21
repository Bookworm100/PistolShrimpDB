# How does this work?
The project has 9 modules total so far, which serve their own purposes and come together to maintain this key value store.

## Module 1: Main
Main.py is the main engine of this key value store. Also, Main.py contains two functions to handle user input to determine the input (JSON) file and the output (storage, usually .bin or .txt) file
### Classes contained:
- renamed: a renamed class storing a tuple of a renamed column the name that that column type now bears.
- PistolShrimpStore - the class that represents the key value store and other variables necessary to keep the value store inserting, deleting, updating, selecting, searching, and finding correctly.

## Module 2: InputFile
InputFile.py holds all information relating to the input file, especially the initial loading of either a json file or existing storage file. Initially, loadFile is called, which calls setupDatabase only if the input file is of JSON form as the file format needs to be converted to a new key value store instead of loading an existing one from a storage file. setupDatabase calls retrieveColumnsData to retrieve columns and data, which is done by find the data.

### Classes contained: 
- InputFile
InputFile Class holds all information relating to the input file, especially the initial loading of either a json file or existing storage file

#### Functions
 - findTheData: locates a source of data (either through a keyword specified or through looking for the largest length of text in the highest level dictionary or list)
- retrieveColumnsData: locates the columns by using a keyword specified by the user if they wish or use a default labeling, and calls find the data, and they retrieve the column labels and data to use
- setupDatabase: sets up the initial key value store if it doesn't exist
- loadFile: loads either the existing storage file or a JSON file specified and in doing so, sets up the intiial key value store

## Module 3: OutputFile
OutputFile.py contains functions specifically to write to the intended storage file. Initially saveChanges writes to the new database file if it doesn't exist. It does some preparation for saving updates, deletes, and inserts, in that order, though based on its current implementation that should not matter.

### Functions: 
- saveChanges - saves changes made to the running key value store
- updateFileWithUpdates - saves all updates to the storage file
- updateFileWithDeletes - saves all deletions to the storage file
- updateFileWithInserts - saves all insertions ot the storage file

## Module 4: Insert
### Classes contained: 
- Insert
Insert Class holds all information relating to inserts, including processing input.

#### Functions:
- generateRandomKey: Generates a random key if the user does not supply one or the user supplied one exists in the key value store (now moved to SharedFunctions as InputFile.py uses it too)
- generateNewRows: Creates a new row/entry based on either a user supplied key
- handleInserts: parses matches to input used to insert a new row

## Module 5: Delete
### Classes contained: 
- Delete
Delete Class holds all information relating to deletes, including processing input.

#### Functions:
- handleDeletes: parses matches to input used to delete an existing row (if the key and its value don't exist, we print an error message instead).

## Module 6: Update
### Classes contained: 
- Update
Update Class holds all information relating to updates, including processing input.

#### Functions:
- handleUpdates: parses matches to input used to update an existing row (if the key and its value don't exist, we print an error message instead).

## Module 7: Select
Select.py contains functions specifically to handle Select commands.

### Functions: 
- handleSelects - Handles all input, including input processing, relating Selects, and passes the appropriate arguments to SharedFunctions.findMatchingKeys if necessary

## Module 8: Search
Search.py contains functions specifically to handle Search and Find input commands.

### Functions: 
- searchList - For each key, col pattern and val pattern specified the user, searchList examines whether these patterns are substrings of corresponding column values of that key (for Search) or of a ratioDistance less than the limit specified of corresponding column values of that key (for Find)
- searchFilter - Filters keys by criteria the user supplied and writes their pertaining information to a buffer string used by handleSearches for output        
- handleSearches - Handles all input, including input processing, relating Searches and Finds, and passes the appropriate arguments to searchFilter

## Module 9: SharedFunctions
SharedFunctions.py contains functions used by multiple other modules.

### Functions:     
- generateRandomKey: Generates a random key if the user does not supply one or the user supplied one exists in the key value store

- spaceMatches - Used to separate out column types and values in commands with commas (Used in Delete.py, Insert.py, Search.py, Selects.py, Update.py)
                       
- conjMatches - Used to separate out column types and values in commands containing ands and ors (Used in Delete.py, Search.py, Select.py)
        
- printSelectsSearches - Prints out select and search statements to either a terminal or file, depending on user preferences
        
- doesColumnTypeValueMatch - Check that a specific row identified by a key keys fits the criteria specified by the combination of the values, with commas or and/ors. (Used by findMatchingKeys, selectKeyswithAndOrs, in SharedFunctions.py)
        
- findMatchingKeys - provides the list of keys which match the criteria associated with a specific set of values
        
- selectKeyswithAndOrs - provides the list of keys which match the criteria associated with a specific set of values with ands/ors